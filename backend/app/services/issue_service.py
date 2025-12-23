"""Issue service for CRUD operations and semantic search"""

from typing import List, Optional, Dict, Any
from supabase import Client
import logging
from datetime import datetime
from app.models.issue import IssueCreate, IssueUpdate, IssueResponse, IssueSearch
from app.services.ml_service import MLService

logger = logging.getLogger(__name__)


class IssueService:
    """Service for issue management and search"""
    
    def __init__(self, db: Client, ml_service: MLService):
        self.db = db
        self.ml_service = ml_service
    
    async def create_issue(self, issue_data: IssueCreate, user_id: str) -> Dict[str, Any]:
        """
        Create a new issue with embedding (with automatic deduplication)
        
        Args:
            issue_data: Issue creation data
            user_id: User creating the issue
            
        Returns:
            Created/updated issue with similar issues
        """
        try:
            # Create embedding text
            issue_dict = issue_data.model_dump()
            embedding_text = self.ml_service.create_embedding_text(issue_dict)
            
            # Generate embedding
            embedding = self.ml_service.generate_embedding(embedding_text)
            
            # Check for duplicates (similarity > 0.9)
            potential_duplicates = await self.find_similar_issues(
                embedding=embedding,
                user_id=user_id,
                threshold=0.9,  # 90% similarity threshold for duplicates
                limit=1
            )
            
            # If high similarity duplicate found, increment occurrence instead of creating
            if potential_duplicates:
                duplicate = potential_duplicates[0]['issue']
                logger.info(f"🔄 Duplicate detected! Updating issue {duplicate['id']} (similarity: {potential_duplicates[0]['similarity']:.2%})")
                
                # Update occurrence count and timestamp
                update_data = {
                    "occurrences": duplicate.get('occurrences', 1) + 1,
                    "last_occurred_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                result = self.db.table("issues").update(update_data).eq("id", duplicate['id']).execute()
                
                if not result.data:
                    raise Exception("Failed to update duplicate issue")
                
                updated_issue = result.data[0]
                
                logger.info(f"✅ Updated duplicate issue: {updated_issue['id']} (occurrences: {updated_issue['occurrences']})")
                
                return {
                    "issue": updated_issue,
                    "is_duplicate": True,
                    "similar_issues": []
                }
            
            # No duplicate found - create new issue
            db_issue = {
                **issue_dict,
                "user_id": user_id,
                "embedding": embedding,
                "embedding_text": embedding_text,
                "status": "open",
                "occurrences": 1,
                "first_occurred_at": datetime.utcnow().isoformat(),
                "last_occurred_at": datetime.utcnow().isoformat()
            }
            
            # Insert into database
            result = self.db.table("issues").insert(db_issue).execute()
            
            if not result.data:
                raise Exception("Failed to create issue")
            
            created_issue = result.data[0]
            
            # Find similar issues (lower threshold for suggestions)
            similar_issues = await self.find_similar_issues(
                embedding=embedding,
                user_id=user_id,
                threshold=0.7,
                limit=5,
                exclude_id=created_issue['id']
            )
            
            logger.info(f"✅ Created new issue: {created_issue['id']}")
            
            return {
                "issue": created_issue,
                "is_duplicate": False,
                "similar_issues": similar_issues
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create issue: {e}")
            raise
    
    async def find_similar_issues(
        self,
        embedding: List[float],
        user_id: str,
        threshold: float = 0.7,
        limit: int = 10,
        exclude_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar issues using vector similarity search
        Falls back to Python-based similarity if pgvector fails
        """
        try:
            # Try pgvector-based search first
            result = self.db.rpc(
                'match_issues',
                {
                    'query_embedding': embedding,
                    'match_threshold': 1 - threshold,
                    'match_count': limit,
                    'user_id_filter': user_id
                }
            ).execute()
            
            similar_issues = []
            for item in result.data:
                if exclude_id and item['id'] == exclude_id:
                    continue
                similarity = 1 - item.get('distance', 1)
                if similarity >= threshold:
                    similar_issues.append({
                        'issue': item,
                        'similarity': round(similarity, 4)
                    })
            
            if similar_issues:
                return similar_issues[:limit]
                
        except Exception as e:
            logger.warning(f"⚠️ pgvector search failed: {e}")
        
        # Fallback: Python-based similarity search
        logger.info("📊 Using Python fallback for similarity search")
        try:
            # Fetch all user's issues with embeddings
            result = self.db.table("issues").select("*").eq("user_id", user_id).execute()
            
            if not result.data:
                logger.info("📊 No issues found for user")
                return []
            
            logger.info(f"📊 Found {len(result.data)} issues in database")
            
            similar_issues = []
            for issue in result.data:
                if exclude_id and issue['id'] == exclude_id:
                    continue
                
                issue_embedding = issue.get('embedding')
                if not issue_embedding:
                    logger.warning(f"⚠️ Issue {issue['id'][:8]} has no embedding")
                    continue
                
                # Log embedding type for debugging
                logger.info(f"📊 Issue {issue['id'][:8]} embedding type: {type(issue_embedding)}, length: {len(str(issue_embedding)[:50])}")
                
                # Compute cosine similarity in Python
                similarity = self.ml_service.compute_similarity(embedding, issue_embedding)
                logger.info(f"📊 Issue {issue['id'][:8]} similarity: {similarity:.4f}")
                
                if similarity >= threshold:
                    similar_issues.append({
                        'issue': issue,
                        'similarity': round(similarity, 4)
                    })
            
            logger.info(f"📊 {len(similar_issues)} issues passed threshold {threshold}")
            
            # Sort by similarity descending
            similar_issues.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_issues[:limit]
            
        except Exception as e:
            logger.error(f"❌ Fallback search also failed: {e}")
            return []
    
    async def search_issues(
        self,
        query: str,
        user_id: str,
        threshold: float = 0.7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search issues by natural language query
        """
        try:
            logger.info(f"🔍 Search query: '{query}' (threshold={threshold}, limit={limit})")
            
            # Generate embedding for query
            query_embedding = self.ml_service.generate_embedding(query)
            logger.info(f"📊 Generated embedding (length={len(query_embedding)}, first 3 vals: {query_embedding[:3]})")
            
            # Find similar issues
            results = await self.find_similar_issues(
                embedding=query_embedding,
                user_id=user_id,
                threshold=threshold,
                limit=limit
            )
            
            logger.info(f"✅ Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            raise
    
    async def get_issue(self, issue_id: str, user_id: str) -> Optional[Dict]:
        """Get issue by ID"""
        try:
            result = self.db.table("issues").select("*").eq("id", issue_id).eq("user_id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Failed to get issue: {e}")
            return None
    
    async def list_issues(
        self,
        user_id: str,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """List issues with filters"""
        try:
            query = self.db.table("issues").select("*").eq("user_id", user_id)
            
            if status:
                query = query.eq("status", status)
            if severity:
                query = query.eq("severity", severity)
            
            result = query.order("created_at", desc=True).limit(limit).offset(offset).execute()
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Failed to list issues: {e}")
            return []
    
    async def update_issue(
        self,
        issue_id: str,
        user_id: str,
        update_data: IssueUpdate
    ) -> Optional[Dict]:
        """Update an issue"""
        try:
            # Get current issue
            issue = await self.get_issue(issue_id, user_id)
            if not issue:
                return None
            
            # Prepare update data
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            
            # If error content changed, regenerate embedding
            if any(k in update_dict for k in ['error_type', 'error_message', 'stack_trace', 'tags']):
                merged_data = {**issue, **update_dict}
                embedding_text = self.ml_service.create_embedding_text(merged_data)
                embedding = self.ml_service.generate_embedding(embedding_text)
                update_dict["embedding"] = embedding
                update_dict["embedding_text"] = embedding_text
            
            # Update in database
            result = self.db.table("issues").update(update_dict).eq("id", issue_id).eq("user_id", user_id).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"❌ Failed to update issue: {e}")
            return None
    
    async def delete_issue(self, issue_id: str, user_id: str) -> bool:
        """Delete an issue"""
        try:
            result = self.db.table("issues").delete().eq("id", issue_id).eq("user_id", user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"❌ Failed to delete issue: {e}")
            return False
