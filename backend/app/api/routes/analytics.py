"""
Analytics endpoints for dashboard metrics.
"""
from datetime import datetime, timedelta
from typing import Optional
import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, extract

from app.core.database import get_db
from app.models.bug import Bug as BugModel
from app.schemas.bug import BugStats, BugTrends, TrendDataPoint

router = APIRouter()


def _percentile(sorted_data: list[float], percentile: int) -> Optional[float]:
    """Calculate the given percentile from a sorted list using linear interpolation."""
    if not sorted_data:
        return None
    n = len(sorted_data)
    idx = (percentile / 100) * (n - 1)
    lower = math.floor(idx)
    upper = math.ceil(idx)
    if lower == upper:
        return round(sorted_data[lower], 1)
    fraction = idx - lower
    value = sorted_data[lower] + fraction * (sorted_data[upper] - sorted_data[lower])
    return round(value, 1)


@router.get("/analytics/overview", response_model=BugStats)
def get_overview_stats(db: Session = Depends(get_db)):
    """
    Get overview statistics for the dashboard.
    
    Returns:
        - Total bugs
        - Open vs closed bugs
        - Average resolution time
        - Bugs by priority
        - Bugs by status
        - Recent activity count
    """
    # Total bugs
    total_bugs = db.query(func.count(BugModel.id)).scalar()
    
    # Open vs closed bugs
    open_bugs = db.query(func.count(BugModel.id)).filter(
        BugModel.status_category != "Done"
    ).scalar()
    closed_bugs = total_bugs - open_bugs
    
    # Average resolution time (in days)
    avg_resolution = db.query(
        func.avg(
            func.extract('epoch', BugModel.resolved_at - BugModel.created_at) / 86400
        )
    ).filter(
        BugModel.resolved_at.isnot(None)
    ).scalar()

    # P50 and P90 resolution time percentiles (in days)
    resolution_rows = db.query(
        func.extract('epoch', BugModel.resolved_at - BugModel.created_at) / 86400
    ).filter(
        BugModel.resolved_at.isnot(None)
    ).all()

    resolution_days_sorted = sorted(row[0] for row in resolution_rows if row[0] is not None)
    p50_resolution = _percentile(resolution_days_sorted, 50)
    p90_resolution = _percentile(resolution_days_sorted, 90)
    
    # Bugs by priority
    priority_counts = db.query(
        BugModel.priority,
        func.count(BugModel.id)
    ).group_by(BugModel.priority).all()
    
    bugs_by_priority = {
        priority or "None": count 
        for priority, count in priority_counts
    }
    
    # Bugs by status
    status_counts = db.query(
        BugModel.status,
        func.count(BugModel.id)
    ).group_by(BugModel.status).all()
    
    bugs_by_status = {
        status: count 
        for status, count in status_counts
    }
    
    # Recent activity (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_activity = db.query(func.count(BugModel.id)).filter(
        BugModel.updated_at >= seven_days_ago
    ).scalar()

    # AI Triage aggregations - Bugs by suggested team
    team_counts = db.query(
        BugModel.triage_team,
        func.count(BugModel.id)
    ).filter(
        BugModel.triage_team.isnot(None)
    ).group_by(BugModel.triage_team).all()

    bugs_by_triage_team = {
        team: count
        for team, count in team_counts
    }

    # AI Triage aggregations - Bugs by category
    category_counts = db.query(
        BugModel.triage_category,
        func.count(BugModel.id)
    ).filter(
        BugModel.triage_category.isnot(None)
    ).group_by(BugModel.triage_category).all()

    bugs_by_triage_category = {
        category: count
        for category, count in category_counts
    }

    # Triage coverage - percentage of bugs that have been triaged
    triaged_count = db.query(func.count(BugModel.id)).filter(
        BugModel.triaged_at.isnot(None)
    ).scalar()
    triage_coverage = round((triaged_count / total_bugs * 100), 1) if total_bugs > 0 else 0

    return BugStats(
        total_bugs=total_bugs,
        open_bugs=open_bugs,
        closed_bugs=closed_bugs,
        avg_resolution_time_days=round(avg_resolution, 1) if avg_resolution else None,
        p50_resolution_time_days=p50_resolution,
        p90_resolution_time_days=p90_resolution,
        bugs_by_priority=bugs_by_priority,
        bugs_by_status=bugs_by_status,
        recent_activity_count=recent_activity,
        bugs_by_triage_team=bugs_by_triage_team,
        bugs_by_triage_category=bugs_by_triage_category,
        triage_coverage=triage_coverage
    )


@router.get("/analytics/trends", response_model=BugTrends)
def get_bug_trends(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get bug trend data for charts.
    
    Args:
        days: Number of days to look back (default: 30)
    
    Returns:
        - Daily created bugs
        - Daily resolved bugs
        - Status distribution over time
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily created bugs
    created_trends = db.query(
        func.date(BugModel.created_at).label('date'),
        func.count(BugModel.id).label('count')
    ).filter(
        BugModel.created_at >= start_date
    ).group_by(
        func.date(BugModel.created_at)
    ).order_by(
        func.date(BugModel.created_at)
    ).all()
    
    daily_created = [
        TrendDataPoint(date=str(date), count=count)
        for date, count in created_trends
    ]
    
    # Daily resolved bugs
    resolved_trends = db.query(
        func.date(BugModel.resolved_at).label('date'),
        func.count(BugModel.id).label('count')
    ).filter(
        BugModel.resolved_at >= start_date,
        BugModel.resolved_at.isnot(None)
    ).group_by(
        func.date(BugModel.resolved_at)
    ).order_by(
        func.date(BugModel.resolved_at)
    ).all()
    
    daily_resolved = [
        TrendDataPoint(date=str(date), count=count)
        for date, count in resolved_trends
    ]
    
    # Status over time (weekly snapshots)
    status_trends = db.query(
        func.date_trunc('week', BugModel.updated_at).label('week'),
        BugModel.status,
        func.count(BugModel.id).label('count')
    ).filter(
        BugModel.updated_at >= start_date
    ).group_by(
        func.date_trunc('week', BugModel.updated_at),
        BugModel.status
    ).order_by(
        func.date_trunc('week', BugModel.updated_at)
    ).all()
    
    status_over_time = [
        TrendDataPoint(date=str(week.date()), count=count, category=status)
        for week, status, count in status_trends
    ]
    
    return BugTrends(
        daily_created=daily_created,
        daily_resolved=daily_resolved,
        status_over_time=status_over_time
    )


@router.get("/analytics/resolution-times")
def get_resolution_times(db: Session = Depends(get_db)):
    """
    Analyze bug resolution times.
    
    Returns:
        - Distribution of resolution times
        - Average by priority
        - Fastest/slowest resolutions
    """
    # Resolution time distribution
    resolution_data = db.query(
        BugModel.jira_key,
        BugModel.priority,
        func.extract('epoch', BugModel.resolved_at - BugModel.created_at).label('seconds')
    ).filter(
        BugModel.resolved_at.isnot(None)
    ).all()
    
    # Convert to days
    resolution_times = [
        {
            "jira_key": key,
            "priority": priority,
            "days": round(seconds / 86400, 1) if seconds else 0
        }
        for key, priority, seconds in resolution_data
    ]
    
    # Average by priority
    avg_by_priority = db.query(
        BugModel.priority,
        func.avg(
            func.extract('epoch', BugModel.resolved_at - BugModel.created_at) / 86400
        ).label('avg_days')
    ).filter(
        BugModel.resolved_at.isnot(None)
    ).group_by(
        BugModel.priority
    ).all()
    
    priority_averages = {
        priority or "None": round(avg_days, 1)
        for priority, avg_days in avg_by_priority if avg_days
    }
    
    return {
        "resolution_times": resolution_times[:100],  # Limit to 100 for performance
        "average_by_priority": priority_averages,
        "total_resolved": len(resolution_times)
    }
