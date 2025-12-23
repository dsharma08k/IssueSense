"""Authentication utilities"""

from fastapi import Header, HTTPException, Depends
from supabase import Client
from app.database import get_db
import logging

logger = logging.getLogger(__name__)


async def get_current_user(
    authorization: str = Header(..., description="Bearer token"),
    db: Client = Depends(get_db)
) -> dict:
    """
    Verify JWT token and return current user
    
    Args:
        authorization: Authorization header with Bearer token
        db: Supabase client
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Extract token
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        
        # Verify token with Supabase
        user_response = db.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return {
            "id": user_response.user.id,
            "email": user_response.user.email,
            "user_metadata": user_response.user.user_metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_optional_user(
    authorization: str = Header(None),
    db: Client = Depends(get_db)
) -> dict | None:
    """Optional authentication (for public endpoints)"""
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization, db)
    except HTTPException:
        return None


async def get_access_token(
    authorization: str = Header(..., description="Bearer token")
) -> str:
    """
    Extract access token from Authorization header
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        Access token string
        
    Raises:
        HTTPException: If header is invalid
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    return authorization.replace("Bearer ", "")
