"""
Jira REST API client for fetching bug data.
"""
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

import requests
from requests.exceptions import RequestException

from app.core.config import settings

logger = logging.getLogger(__name__)


class JiraClient:
    """Client for interacting with Jira REST API."""
    
    def __init__(self):
        self.base_url = settings.JIRA_BASE_URL
        self.project = settings.JIRA_PROJECT
        self.issue_type = settings.JIRA_ISSUE_TYPE
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def search_bugs(
        self,
        max_results: int = 100,
        start_at: int = 0,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for bugs in the Jira project.
        
        Args:
            max_results: Maximum number of results to return
            start_at: Starting index for pagination
            status_filter: Optional status filter (e.g., "!Done" for non-done items)
        
        Returns:
            Dictionary with 'issues', 'total', and 'maxResults' keys
        """
        # Build JQL query
        jql_parts = [
            f"project={self.project}",
            f"type={self.issue_type}"
        ]
        
        if status_filter:
            jql_parts.append(f"statusCategory{status_filter}")
        
        jql = " AND ".join(jql_parts) + " ORDER BY updated DESC"
        
        # API endpoint
        url = f"{self.base_url}/rest/api/2/search"
        
        params = {
            "jql": jql,
            "maxResults": max_results,
            "startAt": start_at,
            "fields": "summary,description,status,priority,created,updated,resolutiondate,components,labels,reporter,assignee"
        }
        
        try:
            logger.info(f"Fetching bugs: {jql}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched {len(data.get('issues', []))} bugs (total: {data.get('total', 0)})")
            
            return data
            
        except RequestException as e:
            logger.error(f"Failed to fetch bugs from Jira: {e}")
            raise
    
    def get_all_bugs(self, batch_size: int = 100, status_filter: Optional[str] = "!=Done") -> List[Dict[str, Any]]:
        """
        Fetch all bugs with pagination.
        
        Args:
            batch_size: Number of bugs to fetch per request
            status_filter: Status filter (e.g., "!=Done" for open bugs only)
        
        Returns:
            List of bug dictionaries
        """
        all_bugs = []
        start_at = 0
        
        while True:
            response = self.search_bugs(
                max_results=batch_size,
                start_at=start_at,
                status_filter=status_filter
            )
            
            issues = response.get("issues", [])
            if not issues:
                break
            
            all_bugs.extend(issues)
            
            total = response.get("total", 0)
            start_at += len(issues)
            
            logger.info(f"Progress: {len(all_bugs)}/{total} bugs fetched")
            
            # Check if we've fetched everything
            if len(all_bugs) >= total:
                break
        
        return all_bugs
    
    def parse_bug(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a Jira issue into our bug format.
        
        Args:
            issue: Raw Jira issue dictionary
        
        Returns:
            Parsed bug dictionary
        """
        fields = issue.get("fields", {})
        
        # Parse dates
        created_at = self._parse_datetime(fields.get("created"))
        updated_at = self._parse_datetime(fields.get("updated"))
        resolved_at = self._parse_datetime(fields.get("resolutiondate"))
        
        # Parse components
        components = fields.get("components", [])
        component = components[0].get("name") if components else None
        
        # Parse labels
        labels = fields.get("labels", [])
        
        # Parse people
        reporter_obj = fields.get("reporter", {})
        reporter = reporter_obj.get("displayName") if reporter_obj else None
        
        assignee_obj = fields.get("assignee", {})
        assignee = assignee_obj.get("displayName") if assignee_obj else None
        
        # Parse status
        status_obj = fields.get("status", {})
        status = status_obj.get("name", "Unknown")
        status_category_obj = status_obj.get("statusCategory", {})
        status_category = status_category_obj.get("name")
        
        # Parse priority
        priority_obj = fields.get("priority", {})
        priority = priority_obj.get("name") if priority_obj else None
        
        return {
            "jira_key": issue.get("key"),
            "jira_id": issue.get("id"),
            "summary": fields.get("summary", ""),
            "description": fields.get("description", ""),
            "status": status,
            "status_category": status_category,
            "priority": priority,
            "created_at": created_at,
            "updated_at": updated_at,
            "resolved_at": resolved_at,
            "component": component,
            "labels": labels,
            "reporter": reporter,
            "assignee": assignee,
            "raw_data": issue  # Store raw data for reference
        }
    
    @staticmethod
    def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        """Parse Jira datetime string."""
        if not date_str:
            return None
        
        try:
            # Jira format: 2024-01-24T10:30:00.000+0000
            return datetime.fromisoformat(date_str.replace("+0000", "+00:00"))
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse datetime '{date_str}': {e}")
            return None


# Global client instance
jira_client = JiraClient()
