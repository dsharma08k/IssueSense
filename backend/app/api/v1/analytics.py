"""Analytics API endpoints"""

from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List
from app.services.analytics_service import AnalyticsService
from app.database import get_db, db
from app.utils.auth import get_current_user, get_access_token
from supabase import Client

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Get dashboard statistics"""
    user_db = db.get_user_client(access_token)
    service = AnalyticsService(user_db)
    stats = await service.get_dashboard_stats(current_user['id'])
    return stats


@router.get("/trends", response_model=List[Dict[str, Any]])
async def get_error_trends(
    days: int = Query(7, ge=1, le=90, description="Number of days"),
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Get error trends over time"""
    user_db = db.get_user_client(access_token)
    service = AnalyticsService(user_db)
    trends = await service.get_error_trends(current_user['id'], days)
    return trends


@router.get("/languages", response_model=List[Dict[str, Any]])
async def get_language_distribution(
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Get distribution of errors by programming language"""
    user_db = db.get_user_client(access_token)
    service = AnalyticsService(user_db)
    distribution = await service.get_language_distribution(current_user['id'])
    return distribution
