"""Issue models"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class SeverityEnum(str, Enum):
    """Issue severity levels"""
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class StatusEnum(str, Enum):
    """Issue status"""
    open = "open"
    resolved = "resolved"
    recurring = "recurring"


class IssueCreate(BaseModel):
    """Schema for creating a new issue"""
    error_type: str = Field(..., max_length=100, description="Type of error (e.g., TypeError)")
    error_message: str = Field(..., max_length=5000, description="Error message")
    stack_trace: Optional[str] = Field(None, max_length=10000, description="Stack trace")
    
    # Context
    file_path: Optional[str] = Field(None, max_length=500)
    line_number: Optional[int] = Field(None, ge=1)
    function_name: Optional[str] = Field(None, max_length=200)
    code_snippet: Optional[str] = Field(None, max_length=2000)
    
    # Environment
    language: Optional[str] = Field(None, max_length=50)
    framework: Optional[str] = Field(None, max_length=100)
    environment: Optional[str] = Field(None, max_length=50)
    os: Optional[str] = Field(None, max_length=50)
    dependencies: Optional[dict] = Field(None, description="Package versions")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, max_length=10)
    severity: SeverityEnum = Field(default=SeverityEnum.medium)
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate and normalize tags"""
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        return [tag.lower().strip() for tag in v if tag.strip()]


class IssueUpdate(BaseModel):
    """Schema for updating an issue"""
    error_type: Optional[str] = Field(None, max_length=100)
    error_message: Optional[str] = Field(None, max_length=5000)
    stack_trace: Optional[str] = Field(None, max_length=10000)
    status: Optional[StatusEnum] = None
    tags: Optional[List[str]] = None
    severity: Optional[SeverityEnum] = None


class IssueResponse(BaseModel):
    """Schema for issue response"""
    id: str
    user_id: str
    team_id: Optional[str] = None
    
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    function_name: Optional[str] = None
    code_snippet: Optional[str] = None
    
    language: Optional[str] = None
    framework: Optional[str] = None
    environment: Optional[str] = None
    os: Optional[str] = None
    dependencies: Optional[dict] = None
    
    tags: List[str] = []
    severity: str
    status: str
    occurrences: int
    
    first_occurred_at: datetime
    last_occurred_at: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class IssueSearch(BaseModel):
    """Schema for search results with similarity"""
    issue: IssueResponse
    similarity: float = Field(..., ge=0, le=1, description="Similarity score (0-1)")
