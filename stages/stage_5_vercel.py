"""
Stage 5: Deploy to Vercel
"""
import os
import time
import requests
from typing import Optional, Dict
from utils.logger import get_logger
from utils.config import VERCEL_TOKEN, VERCEL_TEAM_ID

logger = get_logger('stage_5_vercel')

class VercelStage:
    def __init__(self, app_dir: str, issue_key: str):
        self.app_dir = app_dir
        self.issue_key = issue_key
        self.base_url = 'https://api.vercel.com'
        self.headers = {
            'Authorization': f'Bearer {VERCEL_TOKEN}',
            'Content-Type': 'application/json'
        }
    
    def run(self) -> Optional[Dict]:
        """
        Trigger Vercel deployment and wait for it to be ready
        Returns: Dictionary with deployment URL
        """
        try:
            logger.info(f"Starting Vercel deployment for {self.issue_key}")
            
            # Trigger deployment
            logger.info("Triggering Vercel deployment")
            deployment_url = f"{self.base_url}/v13/deployments"
            
            files_to_deploy = self._get_files()
            
            payload = {
                'name': f'ai-pipeline-{self.issue_key.lower()}',
                'files': files_to_deploy,
                'meta': {
                    'issue_key': self.issue_key
                }
            }
            
            if VERCEL_TEAM_ID:
                payload['teamId'] = VERCEL_TEAM_ID
            
            response = requests.post(deployment_url, json=payload, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to trigger deployment: {response.text}")
                return None
            
            deployment = response.json()
            deployment_id = deployment['id']
            logger.info(f"Deployment triggered with ID: {deployment_id}")
            
            # Poll for deployment status
            logger.info("Polling deployment status...")
            deployment_url_poll = f"{self.base_url}/v13/deployments/{deployment_id}"
            
            max_wait = 300  # 5 minutes
            start_time = time.time()
            ready = False
            live_url = None
            
            while time.time() - start_time < max_wait:
                response = requests.get(deployment_url_poll, headers=self.headers)
                deployment = response.json()
                
                state = deployment.get('state')
                logger.info(f"Deployment state: {state}")
                
                if state == 'READY':
                    live_url = deployment.get('url')
                    if not live_url.startswith('http'):
                        live_url = f"https://{live_url}"
                    ready = True
                    break
                elif state in ['ERROR', 'CANCELED']:
                    logger.error(f"Deployment failed with state: {state}")
                    return None
                
                time.sleep(10)
            
            if not ready:
                logger.error("Deployment timeout - did not reach READY state")
                return None
            
            logger.info(f"Deployment ready at: {live_url}")
            
            # Health check
            logger.info("Running health check...")
            try:
                response = requests.get(live_url, timeout=10)
                if response.status_code == 200:
                    logger.info("Health check passed")
                else:
                    logger.warning(f"Health check returned status {response.status_code}")
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return None
            
            return {
                'status': 'success',
                'deployment_id': deployment_id,
                'url': live_url
            }
        
        except Exception as e:
            logger.error(f"Error in Vercel stage: {e}", exc_info=True)
            return None
    
    def _get_files(self) -> list:
        """Prepare files for deployment"""
        files = []
        for root, dirs, filenames in os.walk(self.app_dir):
            # Skip hidden directories and common build/cache dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            for filename in filenames:
                if filename.startswith('.'):
                    continue
                
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, self.app_dir)
                
                try:
                    with open(filepath, 'rb') as f:
                        content = f.read()
                        files.append({
                            'file': rel_path,
                            'data': content.decode('utf-8') if filename.endswith(('.txt', '.html', '.css', '.js', '.json', '.md')) else content.hex()
                        })
                except:
                    pass
        
        return files

def stage_5_vercel(app_dir: str, issue_key: str):
    """Execute Stage 5"""
    vercel = VercelStage(app_dir, issue_key)
    return vercel.run()
