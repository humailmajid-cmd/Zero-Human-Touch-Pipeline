"""
Stage 7: Send QA report via email
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional
from utils.logger import get_logger
from utils.config import (
    EMAIL_SERVICE, SENDGRID_API_KEY, RESEND_API_KEY,
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
    EMAIL_FROM, EMAIL_TO
)

logger = get_logger('stage_7_email')

class EmailStage:
    def __init__(self, issue_key: str, bug_report_path: str, screenshots: list, test_status: str):
        self.issue_key = issue_key
        self.bug_report_path = bug_report_path
        self.screenshots = screenshots
        self.test_status = test_status
    
    def run(self) -> Optional[bool]:
        """
        Send QA report email with attachments
        Returns: True if successful, False otherwise
        """
        try:
            logger.info(f"Starting email stage for {self.issue_key}")
            
            # Read bug report
            with open(self.bug_report_path, 'r') as f:
                report_content = f.read()
            
            subject = f"QA Report — {self.issue_key} — {self.test_status}"
            
            if EMAIL_SERVICE == 'sendgrid':
                return self._send_via_sendgrid(subject, report_content)
            elif EMAIL_SERVICE == 'resend':
                return self._send_via_resend(subject, report_content)
            else:
                return self._send_via_smtp(subject, report_content)
        
        except Exception as e:
            logger.error(f"Error in email stage: {e}", exc_info=True)
            return False
    
    def _send_via_smtp(self, subject: str, body: str) -> bool:
        """Send via SMTP"""
        try:
            logger.info("Sending via SMTP")
            
            msg = MIMEMultipart()
            msg['From'] = EMAIL_FROM
            msg['To'] = EMAIL_TO
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Attach screenshots
            for screenshot_path in self.screenshots:
                if os.path.exists(screenshot_path):
                    with open(screenshot_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(screenshot_path)}')
                        msg.attach(part)
            
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {EMAIL_TO}")
            return True
        
        except Exception as e:
            logger.error(f"SMTP send failed: {e}")
            return False
    
    def _send_via_sendgrid(self, subject: str, body: str) -> bool:
        """Send via SendGrid"""
        try:
            logger.info("Sending via SendGrid")
            
            import requests
            
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Build attachments
            attachments = []
            for screenshot_path in self.screenshots:
                if os.path.exists(screenshot_path):
                    with open(screenshot_path, 'rb') as f:
                        import base64
                        attachments.append({
                            "content": base64.b64encode(f.read()).decode(),
                            "type": "image/png",
                            "filename": os.path.basename(screenshot_path)
                        })
            
            payload = {
                "personalizations": [{"to": [{"email": EMAIL_TO}]}],
                "from": {"email": EMAIL_FROM},
                "subject": subject,
                "content": [{"type": "text/html", "value": body}],
                "attachments": attachments
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully via SendGrid to {EMAIL_TO}")
                return True
            else:
                logger.error(f"SendGrid API error: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"SendGrid send failed: {e}")
            return False
    
    def _send_via_resend(self, subject: str, body: str) -> bool:
        """Send via Resend"""
        try:
            logger.info("Sending via Resend")
            
            import requests
            
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "from": EMAIL_FROM,
                "to": EMAIL_TO,
                "subject": subject,
                "html": body
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                logger.info(f"Email sent successfully via Resend to {EMAIL_TO}")
                return True
            else:
                logger.error(f"Resend API error: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Resend send failed: {e}")
            return False

def stage_7_email(issue_key: str, bug_report_path: str, screenshots: list, test_status: str):
    """Execute Stage 7"""
    emailer = EmailStage(issue_key, bug_report_path, screenshots, test_status)
    return emailer.run()
