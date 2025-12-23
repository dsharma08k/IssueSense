"""Analytics service for dashboard stats and insights"""

from typing import Dict, Any, List
from supabase import Client
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and insights"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def get_dashboard_stats(self, user_id: str) -> Dict[str, Any]:
        """Get overview statistics for dashboard"""
        try:
            # Get all issues for user
            issues_result = self.db.table("issues")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
            
            issues = issues_result.data
            total_issues = len(issues)
            
            # Count by status
            resolved_issues = sum(1 for i in issues if i.get('status') == 'resolved')
            open_issues = sum(1 for i in issues if i.get('status') == 'open')
            recurring_issues = sum(1 for i in issues if i.get('status') == 'recurring')
            
            # Resolution rate
            resolution_rate = resolved_issues / total_issues if total_issues > 0 else 0.0
            
            # Count by severity
            severity_counts = {
                'critical': sum(1 for i in issues if i.get('severity') == 'critical'),
                'high': sum(1 for i in issues if i.get('severity') == 'high'),
                'medium': sum(1 for i in issues if i.get('severity') == 'medium'),
                'low': sum(1 for i in issues if i.get('severity') == 'low')
            }
            
            # Top error types
            error_type_counts = {}
            for issue in issues:
                error_type = issue.get('error_type', 'Unknown')
                error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
            
            top_error_types = sorted(
                [{'type': k, 'count': v} for k, v in error_type_counts.items()],
                key=lambda x: x['count'],
                reverse=True
            )[:10]
            
            # Total solutions
            solutions_result = self.db.table("solutions")\
                .select("id, issue_id")\
                .execute()
            
            # Filter solutions for user's issues
            user_issue_ids = {i['id'] for i in issues}
            user_solutions = [s for s in solutions_result.data if s['issue_id'] in user_issue_ids]
            total_solutions = len(user_solutions)
            
            return {
                "total_issues": total_issues,
                "open_issues": open_issues,
                "resolved_issues": resolved_issues,
                "recurring_issues": recurring_issues,
                "resolution_rate": round(resolution_rate, 2),
                "total_solutions": total_solutions,
                "issues_by_severity": severity_counts,
                "top_error_types": top_error_types
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get dashboard stats: {e}")
            return {
                "total_issues": 0,
                "open_issues": 0,
                "resolved_issues": 0,
                "recurring_issues": 0,
                "resolution_rate": 0.0,
                "total_solutions": 0,
                "issues_by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "top_error_types": []
            }
    
    async def get_error_trends(
        self,
        user_id: str,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get error trends over time"""
        try:
            # Get issues from last N days
            start_date = datetime.utcnow() - timedelta(days=days)
            
            result = self.db.table("issues")\
                .select("created_at, status, severity")\
                .eq("user_id", user_id)\
                .gte("created_at", start_date.isoformat())\
                .order("created_at")\
                .execute()
            
            issues = result.data
            
            # Group by date
            daily_counts = {}
            for issue in issues:
                date_str = issue['created_at'][:10]  # Get YYYY-MM-DD
                if date_str not in daily_counts:
                    daily_counts[date_str] = {
                        'date': date_str,
                        'total': 0,
                        'resolved': 0,
                        'open': 0
                    }
                
                daily_counts[date_str]['total'] += 1
                if issue.get('status') == 'resolved':
                    daily_counts[date_str]['resolved'] += 1
                elif issue.get('status') == 'open':
                    daily_counts[date_str]['open'] += 1
            
            # Fill in missing dates with zeros
            trend_data = []
            for i in range(days):
                date = (datetime.utcnow() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
                if date in daily_counts:
                    trend_data.append(daily_counts[date])
                else:
                    trend_data.append({
                        'date': date,
                        'total': 0,
                        'resolved': 0,
                        'open': 0
                    })
            
            return trend_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get error trends: {e}")
            return []
    
    async def get_language_distribution(self, user_id: str) -> List[Dict[str, Any]]:
        """Get distribution of errors by programming language"""
        try:
            result = self.db.table("issues")\
                .select("language")\
                .eq("user_id", user_id)\
                .execute()
            
            # Count by language
            language_counts = {}
            for issue in result.data:
                lang = issue.get('language') or 'Unknown'
                language_counts[lang] = language_counts.get(lang, 0) + 1
            
            distribution = [
                {'language': k, 'count': v}
                for k, v in language_counts.items()
            ]
            
            return sorted(distribution, key=lambda x: x['count'], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Failed to get language distribution: {e}")
            return []
