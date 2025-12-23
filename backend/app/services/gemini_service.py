"""Gemini AI service for solution generation"""

import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for AI-powered solution generation using Gemini"""
    
    def __init__(self):
        api_key = settings.gemini_api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')  # Use 1.5 for better quota limits
            self.enabled = True
            logger.info("✅ Gemini AI service initialized")
        else:
            self.enabled = False
            logger.warning("⚠️ Gemini API key not found - AI suggestions disabled")
    
    async def generate_solution(self, issue_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate solution suggestion for an issue using Gemini AI"""
        if not self.enabled:
            return None
        
        try:
            # Build prompt
            prompt = f"""You are an expert programmer helping to solve a coding error.

**Error Details:**
- Type: {issue_data.get('error_type', 'Unknown')}
- Message: {issue_data.get('error_message', 'No message')}
- Language: {issue_data.get('language', 'Unknown')}
- Severity: {issue_data.get('severity', 'medium')}

"""
            
            if issue_data.get('stack_trace'):
                prompt += f"""**Stack Trace:**
{issue_data['stack_trace'][:500]}

"""
            
            if issue_data.get('code_snippet'):
                prompt += f"""**Code Snippet:**
```{issue_data.get('language', '').lower()}
{issue_data['code_snippet']}
```

"""
            
            prompt += """**Task:**
Provide a concise solution to fix this error. Format your response as:

1. **Root Cause:** Brief explanation (1-2 sentences)
2. **Solution:** Step-by-step fix (3-5 steps max)
3. **Code Fix:** Corrected code snippet if applicable

Keep it practical and actionable. Focus on the most common cause."""

            # Generate response
            response = self.model.generate_content(prompt)
            
            if response.text:
                logger.info("✅ Generated AI solution suggestion")
                return {
                    "title": f"AI Suggestion: Fix for {issue_data.get('error_type', 'Error')}",
                    "description": response.text,
                    "ai_generated": True
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to generate AI solution: {e}")
            return None


# Global instance
gemini_service = GeminiService()
