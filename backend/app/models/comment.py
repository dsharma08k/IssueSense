"""Comment models for issue discussions"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CommentBase(BaseModel):
    """Base comment model"""
    content: str = Field(..., min_length=1, max_length=2000, description="Comment content")


class CommentCreate(CommentBase):
    """Model for creating a comment"""
    pass


class CommentUpdate(BaseModel):
    """Model for updating a comment"""
    content: Optional[str] = Field(None, min_length=1, max_length=2000)


class CommentResponse(CommentBase):
    """Model for comment response"""
    id: str
    issue_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
