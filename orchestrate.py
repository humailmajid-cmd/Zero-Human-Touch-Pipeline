"""
Main Orchestration Script - Zero Human Touch Pipeline
Coordinates all stages of the automated delivery pipeline
"""
import os
import sys
import tempfile
import time
from datetime import datetime

# Add stages to path
sys.path.insert(0, os.path.dirname(__file__))

from stages.stage_1_jira_poll import stage_1_poll_jira
from stages.stage_2_build import stage_2_build
from stages.stage_3_tests import stage_3_test
from stages.stage_4_github import stage_4_github
from stages.stage_5_vercel import stage_5_vercel
from stages.stage_6_qa import stage_6_qa
from stages.stage_7_email import stage_7_email
from stages.stage_8_jira_close import stage_8_jira_close
from utils.logger import get_logger
from utils.config import OUTPUT_DIR

logger = get_logger('orchestrator')

class Pipeline:
    def __init__(self):
        self.issue_key = None
        self.requirements = None
        self.output_dir = None
        self.github_result = None
        self.deployment_url = None
        self.qa_result = None
        self.bug_report = None
        self.start_time = datetime.now()
    
    def run(self):
        """Execute the full pipeline"""
        try:
            logger.info("="*60)
            logger.info("ZERO HUMAN TOUCH PIPELINE STARTED")
            logger.info("="*60)
            
            # Stage 1: Poll Jira
            logger.info("[Stage 1] Polling Jira for new stories...")
            jira_result = stage_1_poll_jira()
            
            if not jira_result:
                logger.info("No new stories to process. Pipeline idle.")
                return
            
            self.issue_key = jira_result['issue_key']
            self.requirements = jira_result['requirements']
            self.output_dir = os.path.join(OUTPUT_DIR, self.issue_key)
            
            logger.info(f"Processing issue: {self.issue_key}")
            logger.info(f"Output directory: {self.output_dir}")
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Stage 2: Build
            logger.info("[Stage 2] Building web application...")
            build_result = stage_2_build(self.requirements, self.output_dir)
            
            if not build_result:
                logger.error("Build stage failed")
                self._handle_failure("Build stage failed")
                return
            
            app_dir = build_result.get('output_dir', self.output_dir)
            logger.info(f"Build output directory: {app_dir}")
            
            # Stage 3: Unit Tests
            logger.info("[Stage 3] Running unit tests...")
            test_result = stage_3_test(app_dir)
            
            if not test_result:
                logger.error("Test stage failed")
                self._handle_failure("Test stage failed")
                return
            
            if not test_result.get('all_passed', False):
                logger.warning("Some tests failed")
            else:
                logger.info("All tests passed!")
            
            # Stage 4: GitHub
            logger.info("[Stage 4] Pushing to GitHub and creating PR...")
            github_result = stage_4_github(app_dir, self.issue_key)
            
            if not github_result:
                logger.error("GitHub stage failed")
                self._handle_failure("GitHub stage failed")
                return
            
            logger.info(f"PR URL: {github_result.get('pr_url', 'N/A')}")
            self.github_result = github_result
            
            # Stage 5: Vercel Deployment
            logger.info("[Stage 5] Deploying to Vercel...")
            vercel_result = stage_5_vercel(app_dir, self.issue_key)
            
            if not vercel_result:
                logger.error("Vercel deployment failed")
                self._handle_failure("Vercel deployment failed")
                return
            
            self.deployment_url = vercel_result.get('url')
            logger.info(f"Live URL: {self.deployment_url}")
            
            # Stage 6: QA Testing
            logger.info("[Stage 6] Running Playwright QA tests...")
            qa_dir = os.path.join(self.output_dir, 'qa')
            os.makedirs(qa_dir, exist_ok=True)
            
            qa_result = stage_6_qa(self.deployment_url, self.requirements, qa_dir)
            
            if not qa_result:
                logger.error("QA stage failed")
                self._handle_failure("QA stage failed")
                return
            
            self.qa_result = qa_result
            self.bug_report = qa_result.get('bug_report')
            
            test_status_str = "PASS" if qa_result.get('status') == 'passed' else "FAIL"
            logger.info(f"QA Status: {test_status_str} ({qa_result.get('passed_count')}/{qa_result.get('test_count')})")
            
            # Stage 7: Send Email
            logger.info("[Stage 7] Sending QA report email...")
            email_result = stage_7_email(
                self.issue_key,
                self.bug_report,
                qa_result.get('screenshots', []),
                test_status_str
            )
            
            if not email_result:
                logger.warning("Email stage failed - continuing...")
            else:
                logger.info("Email sent successfully")
            
            # Stage 8: Close Jira
            logger.info("[Stage 8] Closing Jira story...")
            
            with open(self.bug_report, 'r') as f:
                bug_report_content = f.read()
            
            jira_close_result = stage_8_jira_close(
                self.issue_key,
                qa_result.get('status', 'unknown'),
                self.deployment_url,
                bug_report_content
            )
            
            if jira_close_result:
                logger.info("Jira story closed successfully")
            else:
                logger.error("Failed to close Jira story")
            
            # Summary
            elapsed = datetime.now() - self.start_time
            logger.info("="*60)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*60)
            logger.info(f"Issue: {self.issue_key}")
            logger.info(f"Deployment URL: {self.deployment_url}")
            logger.info(f"Total time: {elapsed}")
            logger.info("="*60)
        
        except Exception as e:
            logger.error(f"Fatal error in pipeline: {e}", exc_info=True)
            self._handle_failure(f"Fatal error: {e}")
    
    def _handle_failure(self, error_msg: str):
        """Handle pipeline failures"""
        logger.error(f"Pipeline failed: {error_msg}")
        
        if self.issue_key:
            try:
                from utils.jira_client import JiraClient
                jira = JiraClient()
                
                # Try to transition to appropriate state
                jira.transition_issue(self.issue_key, 'Bug Reported')
                jira.add_comment(self.issue_key, f"❌ Pipeline failed: {error_msg}")
                
                logger.info(f"Updated {self.issue_key} with failure status")
            except Exception as e:
                logger.error(f"Failed to update Jira: {e}")

def main():
    """Entry point"""
    pipeline = Pipeline()
    pipeline.run()

if __name__ == '__main__':
    main()
