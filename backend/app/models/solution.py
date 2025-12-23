"""Solution models"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SolutionCreate(BaseModel):
    """Schema for creating a solution"""
    title: str = Field(..., max_length=200, description="Solution title")
    description: str = Field(..., max_length=5000, description="Detailed description")
    code_fix: Optional[str] = Field(None, max_length=5000, description="Code fix snippet")
    steps: List[str] = Field(default_factory=list, description="Step-by-step instructions")
    tags: List[str] = Field(default_factory=list, max_length=10)


class SolutionUpdate(BaseModel):
    """Schema for updating a solution"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    code_fix: Optional[str] = Field(None, max_length=5000)
    steps: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    verified: Optional[bool] = None


class SolutionResponse(BaseModel):
    """Schema for solution response"""
    id: str
    issue_id: str
    created_by: str
    
    title: str
    description: str
    code_fix: Optional[str] = None
    steps: List[str] = []
    
    effectiveness_score: float
    times_used: int
    success_count: int
    failure_count: int
    
    tags: List[str] = []
    verified: bool
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class SolutionFeedback(BaseModel):
    """Schema for solution feedback"""
    was_helpful: bool = Field(..., description="Whether solution helped")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional feedback comment")
