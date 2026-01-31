"""
GitHub API client for fetching commit data.
"""
import logging
import re
from typing import Optional, Dict, List, Any
from datetime import datetime

import requests
from requests.exceptions import RequestException

from app.core.config import settings

logger = logging.getLogger(__name__)

# Regex pattern to match Jira keys (e.g., MIG-1234, CLOUD-567)
JIRA_KEY_PATTERN = re.compile(r'\b([A-Z]+-\d+)\b')


class GitHubClient:
    """Client for interacting with GitHub REST API."""

    def __init__(self):
        self.base_url = "https://api.github.com"
        self.owner = settings.GITHUB_REPO_OWNER
        self.repo = settings.GITHUB_REPO_NAME
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })
        if settings.GITHUB_TOKEN:
            self.session.headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    def is_available(self) -> bool:
        """Check if GitHub client is configured."""
        return bool(settings.GITHUB_TOKEN)

    def get_commits(
        self,
        per_page: int = 100,
        page: int = 1,
        since: Optional[str] = None,
        until: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch commits from the repository.

        Args:
            per_page: Number of commits per page (max 100)
            page: Page number
            since: Only commits after this date (ISO 8601 format)
            until: Only commits before this date (ISO 8601 format)

        Returns:
            List of commit dictionaries
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/commits"

        params = {
            "per_page": min(per_page, 100),
            "page": page
        }
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        try:
            logger.info(f"Fetching commits from {self.owner}/{self.repo} (page {page})")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            commits = response.json()
            logger.info(f"Fetched {len(commits)} commits")

            return commits

        except RequestException as e:
            logger.error(f"Failed to fetch commits from GitHub: {e}")
            raise

    def get_all_commits(
        self,
        since: Optional[str] = None,
        max_commits: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Fetch all commits with pagination.

        Args:
            since: Only commits after this date (ISO 8601 format)
            max_commits: Maximum number of commits to fetch

        Returns:
            List of commit dictionaries
        """
        all_commits = []
        page = 1

        while len(all_commits) < max_commits:
            commits = self.get_commits(per_page=100, page=page, since=since)

            if not commits:
                break

            all_commits.extend(commits)
            page += 1

            logger.info(f"Progress: {len(all_commits)} commits fetched")

            if len(commits) < 100:  # Last page
                break

        return all_commits[:max_commits]

    def parse_commit(self, commit: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a GitHub commit into our format.

        Args:
            commit: Raw GitHub commit dictionary

        Returns:
            Parsed commit dictionary with Jira keys extracted
        """
        commit_data = commit.get("commit", {})
        author_data = commit_data.get("author", {})

        sha = commit.get("sha", "")
        message = commit_data.get("message", "")

        # Extract Jira keys from commit message
        jira_keys = JIRA_KEY_PATTERN.findall(message)
        # Filter to only include keys from configured project (MIG)
        jira_keys = [key for key in jira_keys if key.startswith(settings.JIRA_PROJECT)]

        # Parse author date
        author_date = None
        if author_data.get("date"):
            try:
                author_date = datetime.fromisoformat(author_data["date"].replace("Z", "+00:00"))
            except ValueError:
                pass

        return {
            "sha": sha,
            "short_sha": sha[:7] if sha else "",
            "message": message,
            "message_headline": message.split("\n")[0][:200] if message else "",
            "author_name": author_data.get("name", ""),
            "author_email": author_data.get("email", ""),
            "authored_at": author_date,
            "url": commit.get("html_url", ""),
            "jira_keys": jira_keys
        }

    @staticmethod
    def extract_jira_keys(text: str) -> List[str]:
        """
        Extract Jira keys from any text.

        Args:
            text: Text to search for Jira keys

        Returns:
            List of Jira keys found
        """
        keys = JIRA_KEY_PATTERN.findall(text)
        return [key for key in keys if key.startswith(settings.JIRA_PROJECT)]


# Global client instance
github_client = GitHubClient()
