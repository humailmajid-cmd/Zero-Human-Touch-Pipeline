"""
Stage 1: Poll Jira for new stories ready to be processed
"""
from typing import Optional, Dict
from utils.logger import get_logger
from utils.jira_client import JiraClient
from utils.config import JIRA_PROJECT_KEY

logger = get_logger('stage_1_jira_poll')

class JiraPollStage:
    def __init__(self, jira_client: JiraClient):
        self.jira = jira_client

    def run(self) -> Optional[Dict]:
        """
        Poll Jira for the oldest 'To Do' story in the project.
        Transitions it to 'In Progress' to claim it, then returns its key and description.
        Returns: {'issue_key': str, 'requirements': str} or None if no stories found.
        """
        try:
            jql = f'project = "{JIRA_PROJECT_KEY}" AND status = "To Do" ORDER BY created ASC'
            issues = self.jira.search_issues(jql)

            if not issues:
                logger.info("No stories in 'To Do' state found")
                return None

            issue = issues[0]
            issue_key = issue['key']
            fields = issue.get('fields', {})

            # Extract plain-text description from Atlassian Document Format
            description = self._extract_description(fields.get('description'))
            summary = fields.get('summary', '')
            requirements = f"# {summary}\n\n{description}" if description else f"# {summary}"

            logger.info(f"Found story {issue_key}: {summary}")

            # Claim the issue by moving it to In Progress
            self.jira.transition_issue(issue_key, 'In Progress')
            self.jira.add_comment(issue_key, "🤖 Pipeline started processing this story.")

            return {
                'issue_key': issue_key,
                'requirements': requirements,
            }

        except Exception as e:
            logger.error(f"Error in Jira poll stage: {e}", exc_info=True)
            return None

    def _extract_description(self, description_field) -> str:
        """Convert Atlassian Document Format description to plain text."""
        if not description_field:
            return ''
        if isinstance(description_field, str):
            return description_field
        # ADF format: {'type': 'doc', 'content': [...]}
        parts = []
        for block in description_field.get('content', []):
            for inline in block.get('content', []):
                text = inline.get('text', '')
                if text:
                    parts.append(text)
            parts.append('\n')
        return ''.join(parts).strip()


def stage_1_poll_jira() -> Optional[Dict]:
    """Execute Stage 1"""
    jira = JiraClient()
    poller = JiraPollStage(jira)
    return poller.run()
