"""API client for backend communication"""

import requests
import streamlit as st
from typing import Dict, List, Optional, Any
from config import API_URL, SESSION_TOKEN_KEY


class APIClient:
    """Client for IssueSense API"""
    
    def __init__(self):
        self.base_url = API_URL
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        headers = {"Content-Type": "application/json"}
        
        if SESSION_TOKEN_KEY in st.session_state:
            token = st.session_state[SESSION_TOKEN_KEY]
            headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    # Issues
    def create_issue(self, issue_data: Dict) -> Dict:
        """Create a new issue"""
        response = self.session.post(
            f"{self.base_url}/api/v1/issues",
            json=issue_data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def search_issues(self, query: str, threshold: float = 0.7, limit: int = 10) -> List[Dict]:
        """Search issues"""
        response = self.session.get(
            f"{self.base_url}/api/v1/issues/search",
            params={"q": query, "threshold": threshold, "limit": limit},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def list_issues(self, status: Optional[str] = None, severity: Optional[str] = None) -> List[Dict]:
        """List all issues"""
        params = {}
        if status:
            params["status"] = status
        if severity:
            params["severity"] = severity
        
        response = self.session.get(
            f"{self.base_url}/api/v1/issues",
            params=params,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_issue(self, issue_id: str) -> Dict:
        """Get issue by ID"""
        response = self.session.get(
            f"{self.base_url}/api/v1/issues/{issue_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def update_issue(self, issue_id: str, update_data: Dict) -> Dict:
        """Update an issue"""
        response = self.session.patch(
            f"{self.base_url}/api/v1/issues/{issue_id}",
            json=update_data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def delete_issue(self, issue_id: str) -> bool:
        """Delete an issue"""
        response = self.session.delete(
            f"{self.base_url}/api/v1/issues/{issue_id}",
            headers=self._get_headers()
        )
        return response.status_code == 204
    
    def batch_update_issues(self, issue_ids: List[str], update_data: Dict) -> Dict:
        """Bulk update multiple issues"""
        response = self.session.post(
            f"{self.base_url}/api/v1/issues/batch/update",
            json={"issue_ids": issue_ids, "update_data": update_data},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def batch_delete_issues(self, issue_ids: List[str]) -> Dict:
        """Bulk delete multiple issues"""
        response = self.session.post(
            f"{self.base_url}/api/v1/issues/batch/delete",
            json={"issue_ids": issue_ids},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def regenerate_embeddings(self) -> Dict:
        """Regenerate embeddings for all issues (fixes search)"""
        response = self.session.post(
            f"{self.base_url}/api/v1/issues/regenerate-embeddings",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # Solutions
    def create_solution(self, issue_id: str, solution_data: Dict) -> Dict:
        """Create a solution"""
        response = self.session.post(
            f"{self.base_url}/api/v1/solutions/issues/{issue_id}/solutions",
            json=solution_data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_solutions(self, issue_id: str) -> List[Dict]:
        """Get solutions for an issue"""
        response = self.session.get(
            f"{self.base_url}/api/v1/solutions/issues/{issue_id}/solutions",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def add_feedback(self, solution_id: str, was_helpful: bool, comment: Optional[str] = None) -> Dict:
        """Add feedback to a solution"""
        feedback_data = {"was_helpful": was_helpful}
        if comment:
            feedback_data["comment"] = comment
        
        response = self.session.post(
            f"{self.base_url}/api/v1/solutions/{solution_id}/feedback",
            json=feedback_data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # Comments
    def create_comment(self, issue_id: str, content: str) -> Dict:
        """Create a comment on an issue"""
        response = self.session.post(
            f"{self.base_url}/api/v1/comments/issues/{issue_id}/comments",
            json={"content": content},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_comments(self, issue_id: str) -> List[Dict]:
        """Get comments for an issue"""
        response = self.session.get(
            f"{self.base_url}/api/v1/comments/issues/{issue_id}/comments",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def update_comment(self, comment_id: str, content: str) -> Dict:
        """Update a comment"""
        response = self.session.patch(
            f"{self.base_url}/api/v1/comments/{comment_id}",
            json={"content": content},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment"""
        response = self.session.delete(
            f"{self.base_url}/api/v1/comments/{comment_id}",
            headers=self._get_headers()
        )
        return response.status_code == 204

    # Export/Import
    def export_json(self) -> bytes:
        """Export issues to JSON"""
        response = self.session.get(
            f"{self.base_url}/api/v1/export/json",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.content
    
    def export_csv(self) -> bytes:
        """Export issues to CSV"""
        response = self.session.get(
            f"{self.base_url}/api/v1/export/csv",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.content
    
    def import_json(self, file_content: bytes) -> Dict:
        """Import issues from JSON file"""
        files = {'file': ('import.json', file_content, 'application/json')}
        response = self.session.post(
            f"{self.base_url}/api/v1/export/import",
            files=files,
            headers={'Authorization': self._get_headers()['Authorization']}  # Don't set Content-Type for multipart
        )
        response.raise_for_status()
        return response.json()

    # AI Solutions
    def suggest_solution(self, issue_id: str) -> Dict:
        """Get AI-generated solution suggestion"""
        response = self.session.post(
            f"{self.base_url}/api/v1/ai/suggest-solution/{issue_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def suggest_and_save_solution(self, issue_id: str) -> Dict:
        """Generate and automatically save AI solution"""
        response = self.session.post(
            f"{self.base_url}/api/v1/ai/suggest-and-save/{issue_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # Analytics
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        response = self.session.get(
            f"{self.base_url}/api/v1/analytics/dashboard",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_trends(self, days: int = 7) -> List[Dict]:
        """Get error trends"""
        response = self.session.get(
            f"{self.base_url}/api/v1/analytics/trends",
            params={"days": days},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_language_distribution(self) -> List[Dict]:
        """Get language distribution"""
        response = self.session.get(
            f"{self.base_url}/api/v1/analytics/languages",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()


# Global API client instance
api_client = APIClient()
