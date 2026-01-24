"""
Pydantic schemas for Bug API.
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class BugBase(BaseModel):
    """Base bug schema with common fields."""
    jira_key: str
    summary: str
    description: Optional[str] = None
    status: str
    status_category: Optional[str] = None
    priority: Optional[str] = None
    component: Optional[str] = None
    reporter: Optional[str] = None
    assignee: Optional[str] = None
    labels: Optional[list[str]] = None


class BugCreate(BugBase):
    """Schema for creating a bug."""
    jira_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    raw_data: Optional[dict[str, Any]] = None


class BugUpdate(BaseModel):
    """Schema for updating a bug (all fields optional)."""
    summary: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    status_category: Optional[str] = None
    priority: Optional[str] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    assignee: Optional[str] = None


class Bug(BugBase):
    """Complete bug schema for API responses."""
    id: int
    jira_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    fetched_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BugList(BaseModel):
    """Schema for paginated bug list."""
    bugs: list[Bug]
    total: int
    page: int
    page_size: int
    total_pages: int


class BugStats(BaseModel):
    """Schema for bug statistics."""
    total_bugs: int
    open_bugs: int
    closed_bugs: int
    avg_resolution_time_days: Optional[float] = None
    bugs_by_priority: dict[str, int]
    bugs_by_status: dict[str, int]
    recent_activity_count: int


class TrendDataPoint(BaseModel):
    """Schema for trend chart data points."""
    date: str
    count: int
    category: Optional[str] = None


class BugTrends(BaseModel):
    """Schema for bug trend analysis."""
    daily_created: list[TrendDataPoint]
    daily_resolved: list[TrendDataPoint]
    status_over_time: list[TrendDataPoint]
