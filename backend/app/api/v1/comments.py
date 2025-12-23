"""Comments API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.comment import CommentCreate, CommentUpdate, CommentResponse
from app.services.comment_service import CommentService
from app.database import get_db, db
from app.utils.auth import get_current_user, get_access_token
from supabase import Client

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/issues/{issue_id}/comments", response_model=dict, status_code=201)
async def create_comment(
    issue_id: str,
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Create a new comment for an issue"""
    user_db = db.get_user_client(access_token)
    service = CommentService(user_db)
    comment = await service.create_comment(issue_id, comment_data, current_user['id'])
    return comment


@router.get("/issues/{issue_id}/comments", response_model=List[dict])
async def get_comments_for_issue(
    issue_id: str,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Get all comments for an issue"""
    user_db = db.get_user_client(access_token)
    service = CommentService(user_db)
    comments = await service.get_comments_for_issue(issue_id)
    return comments


@router.get("/{comment_id}", response_model=dict)
async def get_comment(
    comment_id: str,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Get comment by ID"""
    user_db = db.get_user_client(access_token)
    service = CommentService(user_db)
    comment = await service.get_comment(comment_id)
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return comment


@router.patch("/{comment_id}", response_model=dict)
async def update_comment(
    comment_id: str,
    update_data: CommentUpdate,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Update a comment"""
    user_db = db.get_user_client(access_token)
    service = CommentService(user_db)
    updated = await service.update_comment(comment_id, current_user['id'], update_data)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Comment not found or unauthorized")
    
    return updated


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: str,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Delete a comment"""
    user_db = db.get_user_client(access_token)
    service = CommentService(user_db)
    deleted = await service.delete_comment(comment_id, current_user['id'])
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found or unauthorized")
    
    return None
