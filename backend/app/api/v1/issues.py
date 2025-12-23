"""Issues API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.models.issue import IssueCreate, IssueUpdate, IssueResponse
from app.services.issue_service import IssueService
from app.services.ml_service import get_ml_service, MLService
from app.database import get_db, db
from app.utils.auth import get_current_user, get_access_token
from supabase import Client

router = APIRouter(prefix="/issues", tags=["issues"])


@router.post("", response_model=dict, status_code=201)
async def create_issue(
    issue_data: IssueCreate,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token),
    ml_service: MLService = Depends(get_ml_service)
):
    """Create a new issue with automatic embedding generation"""
    # Create user-specific client with JWT token for RLS
    user_db = db.get_user_client(access_token)
    service = IssueService(user_db, ml_service)
    result = await service.create_issue(issue_data, current_user['id'])
    return result


@router.get("/search", response_model=List[dict])
async def search_issues(
    q: str = Query(..., description="Search query"),
    threshold: float = Query(0.7, ge=0, le=1, description="Similarity threshold"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token),
    ml_service: MLService = Depends(get_ml_service)
):
    """Search issues using semantic similarity"""
    user_db = db.get_user_client(access_token)
    service = IssueService(user_db, ml_service)
    results = await service.search_issues(q, current_user['id'], threshold, limit)
    return results


@router.get("", response_model=List[dict])
async def list_issues(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token),
    ml_service: MLService = Depends(get_ml_service)
):
    """List all issues for current user"""
    user_db = db.get_user_client(access_token)
    service = IssueService(user_db, ml_service)
    issues = await service.list_issues(
        current_user['id'],
        status=status,
        severity=severity,
        limit=limit,
        offset=offset
    )
    return issues


@router.get("/{issue_id}", response_model=dict)
async def get_issue(
    issue_id: str,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token),
    ml_service: MLService = Depends(get_ml_service)
):
    """Get issue by ID"""
    user_db = db.get_user_client(access_token)
    service = IssueService(user_db, ml_service)
    issue = await service.get_issue(issue_id, current_user['id'])
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    return issue


@router.patch("/{issue_id}", response_model=dict)
async def update_issue(
    issue_id: str,
    update_data: IssueUpdate,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token),
    ml_service: MLService = Depends(get_ml_service)
):
    """Update an issue"""
    user_db = db.get_user_client(access_token)
    service = IssueService(user_db, ml_service)
    updated = await service.update_issue(issue_id, current_user['id'], update_data)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    return updated


@router.delete("/{issue_id}", status_code=204)
async def delete_issue(
    issue_id: str,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token),
    ml_service: MLService = Depends(get_ml_service)
):
    """Delete an issue"""
    user_db = db.get_user_client(access_token)
    service = IssueService(user_db, ml_service)
    deleted = await service.delete_issue(issue_id, current_user['id'])
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    return None

# Batch Operations  
@router.post("/batch/update")
async def batch_update_issues(
    issue_ids: List[str],
    update_data: dict,
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Bulk update multiple issues"""
    user_db = db.get_user_client(access_token)
    updated_count = 0
    for issue_id in issue_ids:
        try:
            result = user_db.table("issues").update(update_data).eq("id", issue_id).eq("user_id", current_user['id']).execute()
            if result.data: updated_count += 1
        except: pass
    return {"success": True, "updated": updated_count, "total": len(issue_ids)}

@router.post("/batch/delete")
async def batch_delete_issues(
    issue_ids: List[str],
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Bulk delete multiple issues"""
    user_db = db.get_user_client(access_token)
    deleted_count = 0
    for issue_id in issue_ids:
        try:
            result = user_db.table("issues").delete().eq("id", issue_id).eq("user_id", current_user['id']).execute()
            if result.data: deleted_count += 1
        except: pass
    return {"success": True, "deleted": deleted_count, "total": len(issue_ids)}


@router.post("/regenerate-embeddings")
async def regenerate_embeddings(
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token),
    ml_service: MLService = Depends(get_ml_service)
):
    """Regenerate embeddings for all user's issues (fixes search for old issues)"""
    user_db = db.get_user_client(access_token)
    
    # Get all issues
    result = user_db.table("issues").select("*").eq("user_id", current_user['id']).execute()
    
    if not result.data:
        return {"success": True, "updated": 0, "message": "No issues found"}
    
    updated_count = 0
    for issue in result.data:
        try:
            # Generate embedding text and embedding
            embedding_text = ml_service.create_embedding_text(issue)
            embedding = ml_service.generate_embedding(embedding_text)
            
            # Update issue with new embedding
            user_db.table("issues").update({
                "embedding": embedding,
                "embedding_text": embedding_text
            }).eq("id", issue['id']).execute()
            
            updated_count += 1
        except Exception as e:
            pass  # Skip failed issues
    
    return {"success": True, "updated": updated_count, "total": len(result.data)}

