"""Comment service for issue discussions"""

from typing import List, Optional, Dict, Any
from supabase import Client
import logging
from datetime import datetime
from app.models.comment import CommentCreate, CommentUpdate

logger = logging.getLogger(__name__)


class CommentService:
    """Service for comment management"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def create_comment(
        self,
        issue_id: str,
        comment_data: CommentCreate,
        user_id: str
    ) -> Dict[str, Any]:
        """Create a new comment"""
        try:
            comment_dict = {
                "issue_id": issue_id,
                "user_id": user_id,
                "content": comment_data.content,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.db.table("comments").insert(comment_dict).execute()
            
            if not result.data:
                raise Exception("Failed to create comment")
            
            logger.info(f"✅ Created comment: {result.data[0]['id']}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"❌ Failed to create comment: {e}")
            raise
    
    async def get_comments_for_issue(self, issue_id: str) -> List[Dict[str, Any]]:
        """Get all comments for an issue"""
        try:
            result = self.db.table("comments")\
                .select("*")\
                .eq("issue_id", issue_id)\
                .order("created_at", desc=False)\
                .execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Failed to get comments: {e}")
            return []
    
    async def get_comment(self, comment_id: str) -> Optional[Dict[str, Any]]:
        """Get comment by ID"""
        try:
            result = self.db.table("comments")\
                .select("*")\
                .eq("id", comment_id)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get comment: {e}")
            return None
    
    async def update_comment(
        self,
        comment_id: str,
        user_id: str,
        update_data: CommentUpdate
    ) -> Optional[Dict[str, Any]]:
        """Update a comment"""
        try:
            update_dict = {
                "content": update_data.content,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.db.table("comments")\
                .update(update_dict)\
                .eq("id", comment_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"❌ Failed to update comment: {e}")
            return None
    
    async def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Delete a comment"""
        try:
            result = self.db.table("comments")\
                .delete()\
                .eq("id", comment_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to delete comment: {e}")
            return False
    
    async def get_comment_count(self, issue_id: str) -> int:
        """Get comment count for an issue"""
        try:
            result = self.db.table("comments")\
                .select("id", count="exact")\
                .eq("issue_id", issue_id)\
                .execute()
            
            return result.count if result.count else 0
            
        except Exception as e:
            logger.error(f"❌ Failed to get comment count: {e}")
            return 0
