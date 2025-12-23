"""Export/Import service for data portability"""

from typing import List, Dict, Any
from supabase import Client
import logging
import json
import csv
from io import StringIO
from datetime import datetime

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting and importing issues"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def export_to_json(self, user_id: str) -> Dict[str, Any]:
        """Export all user issues to JSON format"""
        try:
            # Get all issues with solutions and comments
            issues_result = self.db.table("issues")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
            
            issues_data = []
            
            for issue in issues_result.data:
                # Get solutions for this issue
                solutions = self.db.table("solutions")\
                    .select("*")\
                    .eq("issue_id", issue['id'])\
                    .execute()
                
                # Get comments for this issue
                comments = self.db.table("comments")\
                    .select("*")\
                    .eq("issue_id", issue['id'])\
                    .execute()
                
                issue_data = {
                    **issue,
                    "solutions": solutions.data if solutions.data else [],
                    "comments": comments.data if comments.data else []
                }
                issues_data.append(issue_data)
            
            export_data = {
                "version": "2.0",
                "exported_at": datetime.utcnow().isoformat(),
                "total_issues": len(issues_data),
                "issues": issues_data
            }
            
            logger.info(f"✅ Exported {len(issues_data)} issues to JSON")
            return export_data
            
        except Exception as e:
            logger.error(f"❌ Failed to export to JSON: {e}")
            raise
    
    async def export_to_csv(self, user_id: str) -> str:
        """Export issues to CSV format"""
        try:
            # Get all issues
            result = self.db.table("issues")\
                .select("id,error_type,error_message,language,severity,status,created_at,occurrences")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            if not result.data:
                return ""
            
            # Create CSV
            output = StringIO()
            fieldnames = ['id', 'error_type', 'error_message', 'language', 'severity', 'status', 'created_at', 'occurrences']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            writer.writeheader()
            for issue in result.data:
                writer.writerow(issue)
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info(f"✅ Exported {len(result.data)} issues to CSV")
            return csv_content
            
        except Exception as e:
            logger.error(f"❌ Failed to export to CSV: {e}")
            raise
    
    async def import_from_json(self, user_id: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import issues from JSON format"""
        try:
            # Validate format
            if json_data.get("version") != "2.0":
                raise ValueError("Unsupported export version")
            
            issues = json_data.get("issues", [])
            imported_count = 0
            skipped_count = 0
            
            for issue_data in issues:
                try:
                    # Remove nested data
                    solutions = issue_data.pop("solutions", [])
                    comments = issue_data.pop("comments", [])
                    
                    # Remove system fields
                    issue_data.pop("id", None)
                    issue_data.pop("embedding", None)
                    issue_data.pop("embedding_text", None)
                    
                    # Set user_id
                    issue_data["user_id"] = user_id
                    issue_data["created_at"] = datetime.utcnow().isoformat()
                    issue_data["updated_at"] = datetime.utcnow().isoformat()
                    
                    # Insert issue
                    result = self.db.table("issues").insert(issue_data).execute()
                    
                    if result.data:
                        new_issue_id = result.data[0]['id']
                        
                        # Import solutions
                        for sol in solutions:
                            sol.pop("id", None)
                            sol["issue_id"] = new_issue_id
                            sol["user_id"] = user_id
                            self.db.table("solutions").insert(sol).execute()
                        
                        # Import comments
                        for comment in comments:
                            comment.pop("id", None)
                            comment["issue_id"] = new_issue_id
                            comment["user_id"] = user_id
                            self.db.table("comments").insert(comment).execute()
                        
                        imported_count += 1
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    logger.warning(f"⚠️ Skipped issue: {e}")
                    skipped_count += 1
            
            result = {
                "imported": imported_count,
                "skipped": skipped_count,
                "total": len(issues)
            }
            
            logger.info(f"✅ Import complete: {imported_count} imported, {skipped_count} skipped")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to import: {e}")
            raise
