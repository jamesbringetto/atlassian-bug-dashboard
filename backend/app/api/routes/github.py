"""
GitHub integration endpoints.
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.bug import Bug as BugModel, Commit, CommitBugLink
from app.services.github_client import github_client

router = APIRouter()


@router.post("/github/sync")
def sync_github_commits(
    max_commits: int = Query(100, ge=1, le=500, description="Maximum commits to fetch"),
    db: Session = Depends(get_db)
):
    """
    Sync commits from GitHub repository.

    Fetches commits, extracts Jira keys from messages, and links them to bugs.

    Args:
        max_commits: Maximum number of commits to fetch
        db: Database session

    Returns:
        Sync results summary
    """
    if not github_client.is_available():
        raise HTTPException(
            status_code=503,
            detail="GitHub integration unavailable. Set GITHUB_TOKEN environment variable."
        )

    try:
        # Fetch commits from GitHub
        raw_commits = github_client.get_all_commits(max_commits=max_commits)

        created_count = 0
        updated_count = 0
        links_created = 0

        for raw_commit in raw_commits:
            commit_data = github_client.parse_commit(raw_commit)

            # Check if commit exists
            existing_commit = db.query(Commit).filter(
                Commit.sha == commit_data["sha"]
            ).first()

            if existing_commit:
                # Update existing commit (in case message was amended)
                existing_commit.message = commit_data["message"]
                existing_commit.message_headline = commit_data["message_headline"]
                existing_commit.jira_keys = commit_data["jira_keys"]
                updated_count += 1
                commit_obj = existing_commit
            else:
                # Create new commit
                commit_obj = Commit(
                    sha=commit_data["sha"],
                    short_sha=commit_data["short_sha"],
                    message=commit_data["message"],
                    message_headline=commit_data["message_headline"],
                    author_name=commit_data["author_name"],
                    author_email=commit_data["author_email"],
                    authored_at=commit_data["authored_at"],
                    url=commit_data["url"],
                    jira_keys=commit_data["jira_keys"]
                )
                db.add(commit_obj)
                db.flush()  # Get ID assigned
                created_count += 1

            # Create links to bugs for each Jira key
            for jira_key in commit_data["jira_keys"]:
                bug = db.query(BugModel).filter(BugModel.jira_key == jira_key).first()
                if bug:
                    # Check if link already exists
                    existing_link = db.query(CommitBugLink).filter(
                        CommitBugLink.commit_id == commit_obj.id,
                        CommitBugLink.bug_id == bug.id
                    ).first()

                    if not existing_link:
                        link = CommitBugLink(
                            commit_id=commit_obj.id,
                            bug_id=bug.id,
                            jira_key=jira_key
                        )
                        db.add(link)
                        links_created += 1

        db.commit()

        return {
            "status": "success",
            "commits_fetched": len(raw_commits),
            "commits_created": created_count,
            "commits_updated": updated_count,
            "links_created": links_created,
            "message": f"Synced {len(raw_commits)} commits, created {links_created} bug links"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"GitHub sync failed: {str(e)}")


@router.get("/github/commits")
def list_commits(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    jira_key: Optional[str] = Query(None, description="Filter by Jira key"),
    db: Session = Depends(get_db)
):
    """
    List commits with optional filtering by Jira key.

    Args:
        page: Page number
        page_size: Number of items per page
        jira_key: Optional Jira key filter
        db: Database session

    Returns:
        Paginated list of commits
    """
    query = db.query(Commit)

    if jira_key:
        query = query.filter(Commit.jira_keys.contains([jira_key]))

    total = query.count()
    commits = query.order_by(desc(Commit.authored_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "commits": [
            {
                "id": c.id,
                "sha": c.sha,
                "short_sha": c.short_sha,
                "message_headline": c.message_headline,
                "author_name": c.author_name,
                "authored_at": c.authored_at.isoformat() if c.authored_at else None,
                "url": c.url,
                "jira_keys": c.jira_keys or []
            }
            for c in commits
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/bugs/{jira_key}/commits")
def get_bug_commits(jira_key: str, db: Session = Depends(get_db)):
    """
    Get all commits linked to a specific bug.

    Args:
        jira_key: Jira issue key (e.g., MIG-1234)
        db: Database session

    Returns:
        List of commits linked to the bug
    """
    # Find the bug
    bug = db.query(BugModel).filter(BugModel.jira_key == jira_key).first()
    if not bug:
        raise HTTPException(status_code=404, detail=f"Bug {jira_key} not found")

    # Get linked commits
    links = db.query(CommitBugLink).filter(CommitBugLink.bug_id == bug.id).all()
    commit_ids = [link.commit_id for link in links]

    commits = db.query(Commit).filter(Commit.id.in_(commit_ids)).order_by(
        desc(Commit.authored_at)
    ).all()

    return {
        "jira_key": jira_key,
        "commit_count": len(commits),
        "commits": [
            {
                "sha": c.sha,
                "short_sha": c.short_sha,
                "message_headline": c.message_headline,
                "message": c.message,
                "author_name": c.author_name,
                "authored_at": c.authored_at.isoformat() if c.authored_at else None,
                "url": c.url
            }
            for c in commits
        ]
    }


@router.get("/github/status")
def github_status(db: Session = Depends(get_db)):
    """
    Get GitHub integration status and statistics.

    Returns:
        GitHub integration status and commit statistics
    """
    total_commits = db.query(Commit).count()
    commits_with_jira = db.query(Commit).filter(
        Commit.jira_keys != None,
        Commit.jira_keys != []
    ).count()
    total_links = db.query(CommitBugLink).count()

    # Get unique bugs with linked commits
    bugs_with_commits = db.query(CommitBugLink.bug_id).distinct().count()

    return {
        "available": github_client.is_available(),
        "repository": f"{github_client.owner}/{github_client.repo}",
        "statistics": {
            "total_commits": total_commits,
            "commits_with_jira_keys": commits_with_jira,
            "total_links": total_links,
            "bugs_with_commits": bugs_with_commits
        }
    }
