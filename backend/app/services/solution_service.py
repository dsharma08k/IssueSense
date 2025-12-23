"""Solution service for managing solutions and feedback"""

from typing import List, Optional, Dict, Any
from supabase import Client
import logging
from datetime import datetime
from app.models.solution import SolutionCreate, SolutionUpdate, SolutionFeedback

logger = logging.getLogger(__name__)


class SolutionService:
    """Service for solution management"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def create_solution(
        self,
        issue_id: str,
        solution_data: SolutionCreate,
        user_id: str
    ) -> Optional[Dict]:
        """Create a new solution for an issue"""
        try:
            db_solution = {
                **solution_data.model_dump(),
                "issue_id": issue_id,
                "created_by": user_id,
                "effectiveness_score": 0.0,
                "times_used": 0,
                "success_count": 0,
                "failure_count": 0,
                "verified": False
            }
            
            result = self.db.table("solutions").insert(db_solution).execute()
            
            if not result.data:
                raise Exception("Failed to create solution")
            
            logger.info(f"✅ Created solution: {result.data[0]['id']}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"❌ Failed to create solution: {e}")
            raise
    
    async def get_solutions_for_issue(self, issue_id: str) -> List[Dict]:
        """Get all solutions for an issue"""
        try:
            result = self.db.table("solutions")\
                .select("*")\
                .eq("issue_id", issue_id)\
                .order("effectiveness_score", desc=True)\
                .execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Failed to get solutions: {e}")
            return []
    
    async def get_solution(self, solution_id: str) -> Optional[Dict]:
        """Get solution by ID"""
        try:
            result = self.db.table("solutions").select("*").eq("id", solution_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Failed to get solution: {e}")
            return None
    
    async def update_solution(
        self,
        solution_id: str,
        user_id: str,
        update_data: SolutionUpdate
    ) -> Optional[Dict]:
        """Update a solution"""
        try:
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.db.table("solutions")\
                .update(update_dict)\
                .eq("id", solution_id)\
                .eq("created_by", user_id)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"❌ Failed to update solution: {e}")
            return None
    
    async def delete_solution(self, solution_id: str, user_id: str) -> bool:
        """Delete a solution"""
        try:
            result = self.db.table("solutions")\
                .delete()\
                .eq("id", solution_id)\
                .eq("created_by", user_id)\
                .execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"❌ Failed to delete solution: {e}")
            return False
    
    async def add_feedback(
        self,
        solution_id: str,
        user_id: str,
        feedback: SolutionFeedback
    ) -> bool:
        """Add feedback for a solution and update effectiveness score"""
        try:
            # Insert feedback
            feedback_data = {
                "solution_id": solution_id,
                "user_id": user_id,
                "was_helpful": feedback.was_helpful,
                "comment": feedback.comment
            }
            
            self.db.table("solution_feedback").upsert(feedback_data).execute()
            
            # Update solution stats
            solution = await self.get_solution(solution_id)
            if solution:
                times_used = solution['times_used'] + 1
                success_count = solution['success_count'] + (1 if feedback.was_helpful else 0)
                failure_count = solution['failure_count'] + (0 if feedback.was_helpful else 1)
                
                # Calculate effectiveness score
                effectiveness_score = success_count / times_used if times_used > 0 else 0.0
                
                self.db.table("solutions").update({
                    "times_used": times_used,
                    "success_count": success_count,
                    "failure_count": failure_count,
                    "effectiveness_score": round(effectiveness_score, 2),
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", solution_id).execute()
            
            logger.info(f"✅ Added feedback for solution: {solution_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add feedback: {e}")
            return False
    
    async def verify_solution(
        self,
        solution_id: str,
        user_id: str
    ) -> Optional[Dict]:
        """Mark solution as verified"""
        try:
            result = self.db.table("solutions").update({
                "verified": True,
                "verified_by": user_id,
                "verified_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", solution_id).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"❌ Failed to verify solution: {e}")
            return None
