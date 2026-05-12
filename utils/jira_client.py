import os
import requests
from typing import Optional, Dict, List
from utils.config import JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN, JIRA_PROJECT_KEY
from utils.logger import get_logger

logger = get_logger('jira_client')

class JiraClient:
    def __init__(self):
        self.url = JIRA_URL
        self.username = JIRA_USERNAME
        self.api_token = JIRA_API_TOKEN
        self.auth = (self.username, self.api_token)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def search_issues(self, jql: str) -> List[Dict]:
        """Search for issues matching JQL query"""
        try:
            response = requests.get(
                f'{self.url}/rest/api/3/search/jql',
                params={'jql': jql, 'fields': 'summary,description,status,attachment'},
                auth=self.auth,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get('issues', [])
        except Exception as e:
            logger.error(f"Failed to search issues: {e}")
            return []
    
    def get_attachments(self, issue_key: str) -> List[Dict]:
        """Get all attachments for an issue"""
        try:
            response = requests.get(
                f'{self.url}/rest/api/3/issue/{issue_key}',
                auth=self.auth,
                headers=self.headers
            )
            response.raise_for_status()
            fields = response.json().get('fields', {})
            return fields.get('attachment', [])
        except Exception as e:
            logger.error(f"Failed to get attachments for {issue_key}: {e}")
            return []
    
    def download_attachment(self, content_url: str, filename: str) -> Optional[str]:
        """Download attachment and save to file"""
        try:
            response = requests.get(content_url, auth=self.auth)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded attachment to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to download attachment: {e}")
            return None
    
    def transition_issue(self, issue_key: str, transition_name: str) -> bool:
        """Transition an issue to a new state"""
        try:
            # Get available transitions
            response = requests.get(
                f'{self.url}/rest/api/3/issue/{issue_key}/transitions',
                auth=self.auth,
                headers=self.headers
            )
            response.raise_for_status()
            
            transitions = response.json().get('transitions', [])
            transition_id = None
            for t in transitions:
                if t['name'].lower() == transition_name.lower():
                    transition_id = t['id']
                    break
            
            if not transition_id:
                logger.warning(f"Transition '{transition_name}' not found for {issue_key}")
                return False
            
            # Apply transition
            response = requests.post(
                f'{self.url}/rest/api/3/issue/{issue_key}/transitions',
                json={'transition': {'id': transition_id}},
                auth=self.auth,
                headers=self.headers
            )
            response.raise_for_status()
            logger.info(f"Transitioned {issue_key} to {transition_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to transition {issue_key}: {e}")
            return False
    
    def add_comment(self, issue_key: str, comment: str) -> bool:
        """Add a comment to an issue"""
        try:
            response = requests.post(
                f'{self.url}/rest/api/3/issue/{issue_key}/comment',
                json={'body': {'version': 1, 'type': 'doc', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': comment}]}]}},
                auth=self.auth,
                headers=self.headers
            )
            response.raise_for_status()
            logger.info(f"Added comment to {issue_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to add comment to {issue_key}: {e}")
            return False
