"""Groq AI service for solution generation"""

import logging
from typing import Dict, Any, Optional
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)


class GroqService:
    """Service for AI-powered solution generation using Groq"""
    
    def __init__(self):
        api_key = settings.groq_api_key
        if api_key:
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.3-70b-versatile"  # Current supported model
            self.enabled = True
            logger.info("✅ Groq AI service initialized")
        else:
            self.enabled = False
            logger.warning("⚠️ Groq API key not found - AI suggestions disabled")
    
    async def generate_solution(self, issue_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate solution suggestion for an issue using Groq AI"""
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

            # Generate response using Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert programmer who helps solve coding errors concisely."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=1024,
            )
            
            response_text = chat_completion.choices[0].message.content
            
            if response_text:
                logger.info("✅ Generated AI solution suggestion")
                return {
                    "title": f"AI Suggestion: Fix for {issue_data.get('error_type', 'Error')}",
                    "description": response_text,
                    "ai_generated": True
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to generate AI solution: {e}")
            return None


# Global instance
groq_service = GroqService()
