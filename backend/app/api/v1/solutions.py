"""Solutions API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.solution import SolutionCreate, SolutionUpdate, SolutionFeedback, SolutionResponse
from app.services.solution_service import SolutionService
from app.database import get_db, db
from app.utils.auth import get_current_user, get_access_token
from supabase import Client

router = APIRouter(prefix="/solutions", tags=["solutions"])


@router.post("/issues/{issue_id}/solutions", response_model=dict, status_code=201)
async def create_solution(
    issue_id: str,
    solution_data: SolutionCreate,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Create a new solution for an issue"""
    user_db = db.get_user_client(access_token)
    service = SolutionService(user_db)
    solution = await service.create_solution(issue_id, solution_data, current_user['id'])
    return solution


@router.get("/issues/{issue_id}/solutions", response_model=List[dict])
async def get_solutions_for_issue(
    issue_id: str,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Get all solutions for an issue"""
    user_db = db.get_user_client(access_token)
    service = SolutionService(user_db)
    solutions = await service.get_solutions_for_issue(issue_id)
    return solutions


@router.get("/{solution_id}", response_model=dict)
async def get_solution(
    solution_id: str,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Get solution by ID"""
    user_db = db.get_user_client(access_token)
    service = SolutionService(user_db)
    solution = await service.get_solution(solution_id)
    
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    return solution


@router.patch("/{solution_id}", response_model=dict)
async def update_solution(
    solution_id: str,
    update_data: SolutionUpdate,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Update a solution"""
    user_db = db.get_user_client(access_token)
    service = SolutionService(user_db)
    updated = await service.update_solution(solution_id, current_user['id'], update_data)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Solution not found or unauthorized")
    
    return updated


@router.delete("/{solution_id}", status_code=204)
async def delete_solution(
    solution_id: str,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Delete a solution"""
    user_db = db.get_user_client(access_token)
    service = SolutionService(user_db)
    deleted = await service.delete_solution(solution_id, current_user['id'])
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Solution not found or unauthorized")
    
    return None


@router.post("/{solution_id}/feedback", status_code=200)
async def add_feedback(
    solution_id: str,
    feedback: SolutionFeedback,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Add feedback for a solution"""
    user_db = db.get_user_client(access_token)
    service = SolutionService(user_db)
    success = await service.add_feedback(solution_id, current_user['id'], feedback)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add feedback")
    
    return {"message": "Feedback recorded successfully"}


@router.post("/{solution_id}/verify", response_model=dict)
async def verify_solution(
    solution_id: str,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Mark solution as verified"""
    user_db = db.get_user_client(access_token)
    service = SolutionService(user_db)
    verified = await service.verify_solution(solution_id, current_user['id'])
    
    if not verified:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    return verified
