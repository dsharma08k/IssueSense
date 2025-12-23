"""AI Solutions API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.services.groq_service import groq_service
from app.services.solution_service import SolutionService
from app.database import db
from app.utils.auth import get_current_user, get_access_token
from app.models.solution import SolutionCreate

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/suggest-solution/{issue_id}", response_model=dict)
async def suggest_solution(
    issue_id: str,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Generate AI solution suggestion for an issue"""
    user_db = db.get_user_client(access_token)
    
    # Get issue details
    issue_result = user_db.table("issues")\
        .select("*")\
        .eq("id", issue_id)\
        .eq("user_id", current_user['id'])\
        .execute()
    
    if not issue_result.data:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    issue = issue_result.data[0]
    
    # Generate AI suggestion
    suggestion = await groq_service.generate_solution(issue)
    
    if not suggestion:
        raise HTTPException(status_code=503, detail="AI service unavailable or no suggestion generated")
    
    return {
        "success": True,
        "suggestion": suggestion,
        "issue_id": issue_id
    }


@router.post("/suggest-and-save/{issue_id}", response_model=dict)
async def suggest_and_save_solution(
    issue_id: str,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Generate AI solution and automatically save it"""
    user_db = db.get_user_client(access_token)
    
    # Get issue details
    issue_result = user_db.table("issues")\
        .select("*")\
        .eq("id", issue_id)\
        .eq("user_id", current_user['id'])\
        .execute()
    
    if not issue_result.data:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    issue = issue_result.data[0]
    
    # Generate AI suggestion
    suggestion = await groq_service.generate_solution(issue)
    
    if not suggestion:
        raise HTTPException(status_code=503, detail="AI service unavailable")
    
    # Save as solution
    solution_service = SolutionService(user_db)
    solution_data = SolutionCreate(
        title=suggestion['title'],
        description=suggestion['description']
    )
    
    solution = await solution_service.create_solution(
        issue_id,
        solution_data,
        current_user['id']
    )
    
    return {
        "success": True,
        "message": "AI solution generated and saved",
        "solution": solution
    }
