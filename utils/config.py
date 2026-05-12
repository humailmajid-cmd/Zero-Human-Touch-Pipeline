import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Jira Config
JIRA_URL = os.getenv('JIRA_URL')
JIRA_USERNAME = os.getenv('JIRA_USERNAME')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY')

# GitHub Config
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO_OWNER = os.getenv('GITHUB_REPO_OWNER')
GITHUB_REPO_NAME = os.getenv('GITHUB_REPO_NAME')

# Vercel Config
VERCEL_TOKEN = os.getenv('VERCEL_TOKEN')
VERCEL_TEAM_ID = os.getenv('VERCEL_TEAM_ID')

# Email Config
EMAIL_SERVICE = os.getenv('EMAIL_SERVICE', 'sendgrid')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')

# Claude Config
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Pipeline Config
CRON_INTERVAL = int(os.getenv('CRON_INTERVAL', 5))
PIPELINE_LOG_LEVEL = os.getenv('PIPELINE_LOG_LEVEL', 'INFO')

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
