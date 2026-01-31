"""
SQLAlchemy models for bugs.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, ARRAY, JSON, Index, Float
from sqlalchemy.sql import func

from app.core.database import Base


class Bug(Base):
    """Bug model representing a Jira bug issue."""

    __tablename__ = "bugs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Jira identifiers
    jira_key = Column(String(50), unique=True, nullable=False, index=True)
    jira_id = Column(String(50), nullable=True)

    # Basic info
    summary = Column(Text, nullable=False)
    description = Column(Text, nullable=True)

    # Status & Priority
    status = Column(String(50), nullable=False, index=True)
    status_category = Column(String(50), nullable=True)
    priority = Column(String(50), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Categorization
    component = Column(String(200), nullable=True)
    labels = Column(ARRAY(String), nullable=True)

    # People
    reporter = Column(String(200), nullable=True)
    assignee = Column(String(200), nullable=True)

    # Raw data for reference
    raw_data = Column(JSON, nullable=True)

    # Metadata
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # AI Triage fields (populated by Claude Haiku)
    triage_category = Column(String(50), nullable=True, index=True)  # bug, feature_request, etc.
    triage_priority = Column(String(20), nullable=True)  # critical, high, medium, low
    triage_urgency = Column(String(20), nullable=True)  # immediate, soon, normal, backlog
    triage_team = Column(String(50), nullable=True, index=True)  # frontend, backend, etc.
    triage_tags = Column(ARRAY(String), nullable=True)
    triage_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    triage_reasoning = Column(Text, nullable=True)
    triaged_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Bug {self.jira_key}: {self.summary[:50]}>"
    
    @property
    def is_open(self) -> bool:
        """Check if bug is still open."""
        open_statuses = ["Open", "In Progress", "Reopened", "To Do"]
        return self.status in open_statuses
    
    @property
    def resolution_time_days(self) -> Optional[int]:
        """Calculate resolution time in days."""
        if self.resolved_at and self.created_at:
            delta = self.resolved_at - self.created_at
            return delta.days
        return None


# Indexes for common queries
Index("idx_bugs_status_priority", Bug.status, Bug.priority)
Index("idx_bugs_created_updated", Bug.created_at, Bug.updated_at)


class SyncLog(Base):
    """Track sync operations for monitoring and debugging."""

    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    sync_type = Column(String(50), nullable=False)  # "full", "incremental"
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="running")  # running, success, failed

    # Results
    bugs_fetched = Column(Integer, default=0)
    bugs_created = Column(Integer, default=0)
    bugs_updated = Column(Integer, default=0)
    bugs_triaged = Column(Integer, default=0)
    triage_errors = Column(Integer, default=0)

    # Error tracking
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<SyncLog {self.id}: {self.sync_type} - {self.status}>"


class Commit(Base):
    """GitHub commit with linked Jira keys."""

    __tablename__ = "commits"

    id = Column(Integer, primary_key=True, index=True)
    sha = Column(String(40), unique=True, nullable=False, index=True)
    short_sha = Column(String(7), nullable=False)
    message = Column(Text, nullable=False)
    message_headline = Column(String(200), nullable=False)

    # Author info
    author_name = Column(String(200), nullable=True)
    author_email = Column(String(200), nullable=True)
    authored_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # GitHub link
    url = Column(String(500), nullable=True)

    # Linked Jira keys (stored as array for quick access)
    jira_keys = Column(ARRAY(String), nullable=True)

    # Metadata
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Commit {self.short_sha}: {self.message_headline[:50]}>"


class CommitBugLink(Base):
    """Many-to-many link between commits and bugs."""

    __tablename__ = "commit_bug_links"

    id = Column(Integer, primary_key=True, index=True)
    commit_id = Column(Integer, nullable=False, index=True)
    bug_id = Column(Integer, nullable=False, index=True)
    jira_key = Column(String(50), nullable=False, index=True)

    # When this link was created
    linked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# Index for efficient lookups
Index("idx_commit_bug_links_commit_bug", CommitBugLink.commit_id, CommitBugLink.bug_id, unique=True)
