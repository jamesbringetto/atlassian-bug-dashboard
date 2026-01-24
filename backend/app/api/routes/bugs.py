"""
Bug CRUD endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.models.bug import Bug as BugModel
from app.schemas.bug import Bug, BugList, BugCreate
from app.services.jira_client import jira_client

router = APIRouter()


@router.get("/bugs", response_model=BugList)
def list_bugs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search in summary"),
    db: Session = Depends(get_db)
):
    """
    List bugs with pagination and filtering.
    
    Args:
        page: Page number (starts at 1)
        page_size: Number of bugs per page
        status: Filter by status (optional)
        priority: Filter by priority (optional)
        search: Search term for summary (optional)
        db: Database session
    
    Returns:
        Paginated list of bugs
    """
    # Build query
    query = db.query(BugModel)
    
    # Apply filters
    if status:
        query = query.filter(BugModel.status == status)
    if priority:
        query = query.filter(BugModel.priority == priority)
    if search:
        query = query.filter(BugModel.summary.ilike(f"%{search}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    bugs = query.order_by(desc(BugModel.updated_at)).offset((page - 1) * page_size).limit(page_size).all()
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size
    
    return BugList(
        bugs=bugs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/bugs/{jira_key}", response_model=Bug)
def get_bug(jira_key: str, db: Session = Depends(get_db)):
    """
    Get a specific bug by Jira key.
    
    Args:
        jira_key: Jira issue key (e.g., MIG-1234)
        db: Database session
    
    Returns:
        Bug details
    """
    bug = db.query(BugModel).filter(BugModel.jira_key == jira_key).first()
    
    if not bug:
        raise HTTPException(status_code=404, detail=f"Bug {jira_key} not found")
    
    return bug


@router.post("/bugs/sync")
def sync_bugs(
    fetch_all: bool = Query(False, description="Fetch all bugs or just open ones"),
    db: Session = Depends(get_db)
):
    """
    Sync bugs from Jira API to database.
    
    This endpoint:
    1. Fetches bugs from Jira API
    2. Parses and transforms the data
    3. Updates existing bugs or creates new ones
    
    Args:
        fetch_all: If True, fetch all bugs. If False, only fetch open bugs.
        db: Database session
    
    Returns:
        Summary of sync operation
    """
    try:
        # Fetch bugs from Jira
        status_filter = None if fetch_all else "!=Done"
        raw_bugs = jira_client.get_all_bugs(status_filter=status_filter)
        
        # Parse and upsert bugs
        created_count = 0
        updated_count = 0
        
        for raw_bug in raw_bugs:
            bug_data = jira_client.parse_bug(raw_bug)
            
            # Check if bug exists
            existing_bug = db.query(BugModel).filter(
                BugModel.jira_key == bug_data["jira_key"]
            ).first()
            
            if existing_bug:
                # Update existing bug
                for key, value in bug_data.items():
                    setattr(existing_bug, key, value)
                updated_count += 1
            else:
                # Create new bug
                new_bug = BugModel(**bug_data)
                db.add(new_bug)
                created_count += 1
        
        # Commit changes
        db.commit()
        
        return {
            "status": "success",
            "total_fetched": len(raw_bugs),
            "created": created_count,
            "updated": updated_count,
            "message": f"Synced {len(raw_bugs)} bugs from Jira"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/bugs/statuses/list")
def list_statuses(db: Session = Depends(get_db)):
    """Get list of all unique statuses."""
    statuses = db.query(BugModel.status).distinct().all()
    return {"statuses": [s[0] for s in statuses if s[0]]}


@router.get("/bugs/priorities/list")
def list_priorities(db: Session = Depends(get_db)):
    """Get list of all unique priorities."""
    priorities = db.query(BugModel.priority).distinct().all()
    return {"priorities": [p[0] for p in priorities if p[0]]}
