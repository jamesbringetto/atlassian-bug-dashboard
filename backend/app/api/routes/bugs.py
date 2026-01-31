"""
Bug CRUD endpoints.
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.config import settings
from app.models.bug import Bug as BugModel
from app.schemas.bug import Bug, BugList, BugCreate
from app.services.jira_client import jira_client
from app.services.triage_service import triage_service

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
    fetch_all: bool = Query(True, description="Fetch all bugs including closed ones"),
    auto_triage: bool = Query(True, description="Auto-triage new bugs with Claude AI"),
    triage_limit: int = Query(20, ge=0, le=100, description="Max bugs to triage per sync (0 = unlimited)"),
    db: Session = Depends(get_db)
):
    """
    Sync bugs from Jira API to database.

    This endpoint:
    1. Fetches bugs from Jira API
    2. Parses and transforms the data
    3. Updates existing bugs or creates new ones
    4. Optionally auto-triages new bugs with Claude AI

    Args:
        fetch_all: If True, fetch all bugs. If False, only fetch open bugs.
        auto_triage: If True, automatically triage new/untriaged bugs.
        triage_limit: Maximum number of bugs to triage per sync (default 20, 0 = unlimited).
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
        bugs_to_triage = []

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
                # Add to triage queue if not yet triaged
                if auto_triage and existing_bug.triaged_at is None:
                    bugs_to_triage.append(existing_bug)
            else:
                # Create new bug
                new_bug = BugModel(**bug_data)
                db.add(new_bug)
                db.flush()  # Get the ID assigned
                created_count += 1
                # Add new bugs to triage queue
                if auto_triage:
                    bugs_to_triage.append(new_bug)

        # Auto-triage bugs if enabled and service is available
        triaged_count = 0
        triage_errors = 0
        triage_skipped = 0

        if auto_triage and settings.TRIAGE_ENABLED and triage_service.is_available():
            for bug in bugs_to_triage:
                # Stop if we've reached the triage limit (0 = unlimited)
                if triage_limit > 0 and triaged_count >= triage_limit:
                    triage_skipped = len(bugs_to_triage) - triaged_count - triage_errors
                    break
                try:
                    result = triage_service.triage_bug(
                        summary=bug.summary,
                        description=bug.description,
                        current_priority=bug.priority,
                        component=bug.component,
                        labels=bug.labels
                    )
                    if result:
                        bug.triage_category = result.category
                        bug.triage_priority = result.priority_recommendation
                        bug.triage_urgency = result.urgency
                        bug.triage_team = result.suggested_team
                        bug.triage_tags = result.tags
                        bug.triage_confidence = result.confidence
                        bug.triage_reasoning = result.reasoning
                        bug.triaged_at = datetime.now(timezone.utc)
                        triaged_count += 1
                except Exception:
                    triage_errors += 1

        # Commit changes
        db.commit()

        return {
            "status": "success",
            "total_fetched": len(raw_bugs),
            "created": created_count,
            "updated": updated_count,
            "triaged": triaged_count,
            "triage_errors": triage_errors,
            "triage_skipped": triage_skipped,
            "message": f"Synced {len(raw_bugs)} bugs from Jira, triaged {triaged_count} bugs" + (f" ({triage_skipped} skipped due to limit)" if triage_skipped > 0 else "")
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


@router.post("/bugs/{jira_key}/triage")
def triage_bug(
    jira_key: str,
    force: bool = Query(False, description="Force re-triage even if already triaged"),
    db: Session = Depends(get_db)
):
    """
    Manually trigger AI triage for a specific bug.

    Args:
        jira_key: Jira issue key (e.g., MIG-1234)
        force: If True, re-triage even if already triaged
        db: Database session

    Returns:
        Triage result
    """
    # Check if triage service is available
    if not triage_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Triage service unavailable. Check ANTHROPIC_API_KEY configuration."
        )

    # Find the bug
    bug = db.query(BugModel).filter(BugModel.jira_key == jira_key).first()
    if not bug:
        raise HTTPException(status_code=404, detail=f"Bug {jira_key} not found")

    # Check if already triaged
    if bug.triaged_at and not force:
        return {
            "status": "already_triaged",
            "jira_key": jira_key,
            "triaged_at": bug.triaged_at.isoformat(),
            "triage": {
                "category": bug.triage_category,
                "priority": bug.triage_priority,
                "urgency": bug.triage_urgency,
                "team": bug.triage_team,
                "tags": bug.triage_tags,
                "confidence": bug.triage_confidence,
                "reasoning": bug.triage_reasoning
            }
        }

    # Perform triage
    result = triage_service.triage_bug(
        summary=bug.summary,
        description=bug.description,
        current_priority=bug.priority,
        component=bug.component,
        labels=bug.labels
    )

    if not result:
        raise HTTPException(status_code=500, detail="Triage failed")

    # Update bug with triage results
    bug.triage_category = result.category
    bug.triage_priority = result.priority_recommendation
    bug.triage_urgency = result.urgency
    bug.triage_team = result.suggested_team
    bug.triage_tags = result.tags
    bug.triage_confidence = result.confidence
    bug.triage_reasoning = result.reasoning
    bug.triaged_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "status": "triaged",
        "jira_key": jira_key,
        "triaged_at": bug.triaged_at.isoformat(),
        "triage": {
            "category": result.category,
            "priority": result.priority_recommendation,
            "urgency": result.urgency,
            "team": result.suggested_team,
            "tags": result.tags,
            "confidence": result.confidence,
            "reasoning": result.reasoning
        }
    }


@router.post("/bugs/triage/batch")
def batch_triage_bugs(
    limit: int = Query(20, ge=1, le=100, description="Max bugs to triage"),
    db: Session = Depends(get_db)
):
    """
    Triage untriaged bugs already in the database (no Jira fetch).

    This is much faster than sync with auto_triage since it skips
    the Jira API calls entirely.

    Args:
        limit: Maximum number of bugs to triage (default 20, max 100)
        db: Database session

    Returns:
        Triage results summary
    """
    # Check if triage service is available
    if not triage_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Triage service unavailable. Check ANTHROPIC_API_KEY configuration."
        )

    # Get untriaged bugs from database
    untriaged_bugs = db.query(BugModel).filter(
        BugModel.triaged_at.is_(None)
    ).limit(limit).all()

    if not untriaged_bugs:
        return {
            "status": "success",
            "triaged": 0,
            "errors": 0,
            "remaining": 0,
            "message": "No untriaged bugs found"
        }

    triaged_count = 0
    error_count = 0

    for bug in untriaged_bugs:
        try:
            result = triage_service.triage_bug(
                summary=bug.summary,
                description=bug.description,
                current_priority=bug.priority,
                component=bug.component,
                labels=bug.labels
            )
            if result:
                bug.triage_category = result.category
                bug.triage_priority = result.priority_recommendation
                bug.triage_urgency = result.urgency
                bug.triage_team = result.suggested_team
                bug.triage_tags = result.tags
                bug.triage_confidence = result.confidence
                bug.triage_reasoning = result.reasoning
                bug.triaged_at = datetime.now(timezone.utc)
                triaged_count += 1
        except Exception:
            error_count += 1

    db.commit()

    # Count remaining untriaged
    remaining = db.query(BugModel).filter(BugModel.triaged_at.is_(None)).count()

    return {
        "status": "success",
        "triaged": triaged_count,
        "errors": error_count,
        "remaining": remaining,
        "message": f"Triaged {triaged_count} bugs, {remaining} remaining"
    }


@router.get("/bugs/triage/status")
def get_triage_status(db: Session = Depends(get_db)):
    """
    Get triage service status and statistics.

    Returns:
        Triage service status and bug triage statistics
    """
    total_bugs = db.query(BugModel).count()
    triaged_bugs = db.query(BugModel).filter(BugModel.triaged_at.isnot(None)).count()
    untriaged_bugs = total_bugs - triaged_bugs

    # Get triage category distribution
    category_counts = {}
    categories = db.query(
        BugModel.triage_category,
        func.count(BugModel.id)
    ).filter(
        BugModel.triage_category.isnot(None)
    ).group_by(BugModel.triage_category).all()
    for cat, count in categories:
        category_counts[cat] = count

    # Get triage team distribution
    team_counts = {}
    teams = db.query(
        BugModel.triage_team,
        func.count(BugModel.id)
    ).filter(
        BugModel.triage_team.isnot(None)
    ).group_by(BugModel.triage_team).all()
    for team, count in teams:
        team_counts[team] = count

    return {
        "service_available": triage_service.is_available(),
        "triage_enabled": settings.TRIAGE_ENABLED,
        "statistics": {
            "total_bugs": total_bugs,
            "triaged_bugs": triaged_bugs,
            "untriaged_bugs": untriaged_bugs,
            "triage_rate": round(triaged_bugs / total_bugs * 100, 1) if total_bugs > 0 else 0
        },
        "by_category": category_counts,
        "by_team": team_counts
    }
