"""
Automatic ticket triage service using Claude Haiku.
"""
import logging
from typing import Optional
from pydantic import BaseModel

import anthropic

from app.core.config import settings

logger = logging.getLogger(__name__)


class TriageResult(BaseModel):
    """Structured triage result from Claude."""
    category: str  # e.g., "bug", "feature_request", "documentation", "performance", "security"
    priority_recommendation: str  # "critical", "high", "medium", "low"
    urgency: str  # "immediate", "soon", "normal", "backlog"
    suggested_team: str  # e.g., "frontend", "backend", "infrastructure", "security", "data"
    tags: list[str]  # Auto-generated tags for categorization
    confidence: float  # 0.0 to 1.0 confidence in the triage
    reasoning: str  # Brief explanation of the triage decision


class TriageService:
    """Service for automatic ticket triage using Claude Haiku."""

    TRIAGE_PROMPT = """You are an expert bug triage specialist for a software development team. Analyze the following bug ticket and provide a structured triage assessment.

## Bug Ticket
**Summary:** {summary}

**Description:** {description}

**Current Priority (from Jira):** {current_priority}
**Component:** {component}
**Labels:** {labels}

## Your Task
Analyze this ticket and provide triage information. Consider:
1. **Category**: What type of issue is this? (bug, feature_request, documentation, performance, security, ui_ux, data_issue, integration)
2. **Priority Recommendation**: Based on potential impact and severity (critical, high, medium, low)
3. **Urgency**: How soon should this be addressed? (immediate, soon, normal, backlog)
4. **Suggested Team**: Which team should handle this? (frontend, backend, infrastructure, security, data, platform, mobile, qa)
5. **Tags**: 3-5 relevant tags for categorization
6. **Confidence**: Your confidence in this assessment (0.0-1.0)
7. **Reasoning**: Brief 1-2 sentence explanation

Respond with ONLY valid JSON matching this exact structure:
{{
  "category": "string",
  "priority_recommendation": "string",
  "urgency": "string",
  "suggested_team": "string",
  "tags": ["string"],
  "confidence": 0.0,
  "reasoning": "string"
}}"""

    def __init__(self):
        self.client = None
        self._initialized = False

    def _ensure_client(self) -> bool:
        """Initialize the Anthropic client if API key is available."""
        if self._initialized:
            return self.client is not None

        self._initialized = True

        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not set - triage service disabled")
            return False

        try:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            logger.info("Anthropic client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            return False

    def is_available(self) -> bool:
        """Check if the triage service is available."""
        return self._ensure_client()

    def triage_bug(
        self,
        summary: str,
        description: Optional[str] = None,
        current_priority: Optional[str] = None,
        component: Optional[str] = None,
        labels: Optional[list[str]] = None
    ) -> Optional[TriageResult]:
        """
        Triage a single bug using Claude Haiku.

        Args:
            summary: Bug summary/title
            description: Bug description (can be None or empty)
            current_priority: Current Jira priority
            component: Jira component
            labels: Jira labels

        Returns:
            TriageResult with triage data, or None if triage fails
        """
        if not self._ensure_client():
            return None

        # Prepare the prompt
        prompt = self.TRIAGE_PROMPT.format(
            summary=summary,
            description=description or "No description provided",
            current_priority=current_priority or "Not set",
            component=component or "Not assigned",
            labels=", ".join(labels) if labels else "None"
        )

        try:
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse the response
            response_text = message.content[0].text

            # Parse JSON from response
            import json
            triage_data = json.loads(response_text)

            # Validate and create result
            result = TriageResult(
                category=triage_data.get("category", "unknown"),
                priority_recommendation=triage_data.get("priority_recommendation", "medium"),
                urgency=triage_data.get("urgency", "normal"),
                suggested_team=triage_data.get("suggested_team", "unassigned"),
                tags=triage_data.get("tags", []),
                confidence=min(1.0, max(0.0, float(triage_data.get("confidence", 0.5)))),
                reasoning=triage_data.get("reasoning", "")
            )

            logger.info(f"Triaged bug: category={result.category}, priority={result.priority_recommendation}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse triage response as JSON: {e}")
            return None
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error during triage: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during triage: {e}")
            return None

    def triage_bugs_batch(
        self,
        bugs: list[dict]
    ) -> dict[str, Optional[TriageResult]]:
        """
        Triage multiple bugs.

        Args:
            bugs: List of bug dictionaries with keys: jira_key, summary, description, priority, component, labels

        Returns:
            Dictionary mapping jira_key to TriageResult (or None if triage failed)
        """
        results = {}

        for bug in bugs:
            jira_key = bug.get("jira_key", "unknown")
            result = self.triage_bug(
                summary=bug.get("summary", ""),
                description=bug.get("description"),
                current_priority=bug.get("priority"),
                component=bug.get("component"),
                labels=bug.get("labels")
            )
            results[jira_key] = result

        triaged_count = sum(1 for r in results.values() if r is not None)
        logger.info(f"Batch triage complete: {triaged_count}/{len(bugs)} bugs triaged")

        return results


# Global service instance
triage_service = TriageService()
