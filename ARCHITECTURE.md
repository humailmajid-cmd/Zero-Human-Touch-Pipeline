# Architecture & Project Structure

## Overview

The Zero Human Touch Pipeline is a fully automated, event-driven software delivery system that:

1. **Monitors** Jira for new stories with a specific label
2. **Orchestrates** an 8-stage automated workflow
3. **Builds**, **tests**, **deploys**, and **verifies** web applications
4. **Reports** results and closes the loop in Jira

All without human intervention after initial story creation.

## Directory Structure

```
pipeline/
├── orchestrate.py              # Main pipeline orchestrator
├── scheduler.py                # Cron job runner (every 5 min)
├── setup.py                    # Initial setup helper
│
├── stages/                     # Individual pipeline stages
│   ├── __init__.py
│   ├── stage_1_jira_poll.py   # Poll Jira for new stories
│   ├── stage_2_build.py        # Build web app
│   ├── stage_3_tests.py        # Run unit tests
│   ├── stage_4_github.py       # Push to GitHub & PR
│   ├── stage_5_vercel.py       # Deploy to Vercel
│   ├── stage_6_qa.py           # Playwright QA testing
│   ├── stage_7_email.py        # Send email report
│   └── stage_8_jira_close.py  # Update Jira & close
│
├── utils/                      # Shared utilities
│   ├── __init__.py
│   ├── config.py              # Configuration from .env
│   ├── logger.py              # Logging setup
│   └── jira_client.py         # Jira API client
│
├── logs/                       # Pipeline execution logs
│   └── YYYYMMDD.log
│
├── output/                     # Built applications
│   └── AI-XXXX/
│       ├── (built app files)
│       ├── test-results.txt
│       └── qa/
│           ├── bug-report.md
│           └── (screenshots)
│
├── .env.example               # Environment template
├── .env                       # Environment config (secrets)
├── .gitignore
├── requirements.txt           # Python dependencies
├── package.json              # Node dependencies
├── README.md                 # Full documentation
├── QUICKSTART.md             # Quick start guide
└── this file                 # Architecture docs
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    JIRA STORY CREATED                       │
│  Title: [AI-PIPELINE] Brief description                     │
│  Label: ai-ready                                            │
│  Attachment: requirements.md                                │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │  SCHEDULER (every 5 minutes)   │
        │  - Poll Jira with JQL          │
        │  - Find ai-ready stories       │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────────────┐
        │  STAGE 1: JIRA POLL                    │
        │  - Download requirements.md             │
        │  - Transition to In Progress            │
        │  - Return issue_key + requirements      │
        └────────────────┬────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────┐
        │  STAGE 2: BUILD                              │
        │  - External agent reads requirements           │
        │  - Builds working web app                     │
        │  - Outputs to directory                       │
        └────────────────┬──────────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────┐
        │  STAGE 3: UNIT TESTS                         │
        │  - Detect test framework (Jest/pytest)        │
        │  - Write meaningful tests                     │
        │  - Run until all pass (max 5 iterations)      │
        │  - Save results to test-results.txt           │
        └────────────────┬──────────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────┐
        │  STAGE 4: GITHUB                             │
        │  - Init git repo                              │
        │  - Create feature branch                      │
        │  - Commit & push                              │
        │  - Open Pull Request                          │
        └────────────────┬──────────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────┐
        │  STAGE 5: VERCEL DEPLOYMENT                  │
        │  - Trigger deployment                         │
        │  - Poll status (max 5 minutes)                │
        │  - Verify health check                        │
        │  - Extract live URL                           │
        └────────────────┬──────────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────┐
        │  STAGE 6: PLAYWRIGHT QA                      │
        │  - Open live deployment URL                   │
        │  - Test acceptance criteria                   │
        │  - Capture console errors                     │
        │  - Take screenshots                           │
        │  - Generate bug report                        │
        └────────────────┬──────────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────┐
        │  STAGE 7: EMAIL REPORT                       │
        │  - Send bug report to EMAIL_TO                │
        │  - Attach screenshots                         │
        │  - Include test results                       │
        └────────────────┬──────────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────┐
        │  STAGE 8: JIRA CLOSE                         │
        │  - Transition to Done (pass) or              │
        │    Bug Reported (fail)                        │
        │  - Add comment with URL & summary             │
        │  - Story complete                             │
        └────────────────┬──────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │  PIPELINE COMPLETE  │
              │  Story in terminal  │
              │  state (Done or     │
              │  Bug Reported)      │
              └─────────────────────┘
```

## Core Components

### 1. Orchestrator (`orchestrate.py`)

**Purpose:** Main entry point that coordinates all stages

**Key Class:** `Pipeline`

- Calls stages sequentially
- Handles errors gracefully
- Logs all progress
- Manages temporary state
- Updates Jira on failures

**Flow:**

```python
pipeline = Pipeline()
pipeline.run()
  → stage_1_poll_jira()
  → stage_2_build()
  → stage_3_test()
  → stage_4_github()
  → stage_5_vercel()
  → stage_6_qa()
  → stage_7_email()
  → stage_8_jira_close()
```

### 2. Scheduler (`scheduler.py`)

**Purpose:** Run orchestrator on a schedule

**Features:**

- Polls Jira every 5 minutes (configurable)
- Runs indefinitely in background
- Logs all execution
- Handles interrupts gracefully

**Usage:**

```bash
python scheduler.py  # Runs forever
```

### 3. Stages (Individual Modules)

Each stage is an independent module with:

- Clear input/output contracts
- Error handling with logging
- Result dictionaries for passing data
- No side effects outside their scope

#### Stage 1: Jira Poll

```
Input: None
Output: {
  issue_key: str,
  requirements: str,
  issue_title: str,
  temp_dir: str
}
```

#### Stage 2: Build

```
Input: requirements, output_dir
Output: {
  status: "pending",
  output_dir: str,
  build_script: str
}
```

#### Stage 3: Tests

```
Input: app_dir
Output: {
  status: "passed"|"failed",
  test_results_file: str,
  all_passed: bool
}
```

#### Stage 4: GitHub

```
Input: app_dir, issue_key
Output: {
  status: "success",
  branch: str,
  pr_url: str,
  commit_message: str
}
```

#### Stage 5: Vercel

```
Input: app_dir, issue_key
Output: {
  status: "success",
  deployment_id: str,
  url: str
}
```

#### Stage 6: QA

```
Input: deployment_url, requirements, output_dir
Output: {
  status: "passed"|"failed",
  test_count: int,
  passed_count: int,
  failed_count: int,
  bug_report: str,
  screenshots: [str],
  console_errors: [{type, text}]
}
```

#### Stage 7: Email

```
Input: issue_key, bug_report_path, screenshots, test_status
Output: bool (success/failure)
```

#### Stage 8: Jira Close

```
Input: issue_key, test_status, deployment_url, bug_report_content
Output: bool (success/failure)
```

### 4. Utilities

#### `config.py`

- Loads environment variables from `.env`
- Provides centralized configuration
- All secrets and credentials

#### `logger.py`

- Sets up logging with file and console handlers
- Logs to `logs/YYYYMMDD.log`
- Includes timestamps and levels

#### `jira_client.py`

- Wraps Jira REST API v3
- Methods: search, download, transition, comment
- Handles authentication
- Error handling & logging

## Error Handling Strategy

Every stage has three-level error handling:

```python
try:
    result = do_something()
    if result is None:
        logger.warning("Stage failed")
        return None
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return None
```

If any stage fails:

1. Error is logged with context
2. Jira is updated (if issue_key known)
3. Story moved to appropriate state (Bug Reported)
4. Pipeline continues to Stage 8 (close)
5. No silent failures

## Configuration Management

### Environment Variables (`.env`)

Required:

```env
JIRA_URL=https://...
JIRA_USERNAME=...
JIRA_API_TOKEN=...
GITHUB_TOKEN=...
VERCEL_TOKEN=...
EMAIL_*=...
```

Optional:

```env
CRON_INTERVAL=5
PIPELINE_LOG_LEVEL=INFO
```

All loaded in `utils/config.py` at startup.

### Paths

```python
BASE_DIR = pipeline/
OUTPUT_DIR = pipeline/output/
LOG_DIR = pipeline/logs/
```

Each issue gets its own directory:

```
output/AI-1234/
  ├── (built files)
  ├── test-results.txt
  └── qa/
      ├── bug-report.md
      └── screenshots/
```

## API Integration Points

### Jira REST API v3

```
GET /rest/api/3/search?jql=...              # Find issues
GET /rest/api/3/issue/{key}                  # Get issue details
GET /rest/api/3/attachment/content/{id}      # Download file
POST /rest/api/3/issue/{key}/transitions     # Change status
POST /rest/api/3/issue/{key}/comment         # Add comment
```

### GitHub REST API

```
Uses gh CLI for simplicity:
- git push
- gh pr create
```

### Vercel REST API

```
POST /v13/deployments                    # Trigger deployment
GET /v13/deployments/{id}                # Poll status
```

### Playwright

```
browser.new_page()
page.goto(url)
page.screenshot()
page.on('console', handler)
page.query_selector()
```

## Logging

All logs go to `logs/YYYYMMDD.log`:

```
2025-05-07 14:32:15 - orchestrator - INFO - [Stage 1] Polling Jira for new stories...
2025-05-07 14:32:16 - jira_client - INFO - Found 1 ai-ready story(ies)
2025-05-07 14:32:17 - stage_1_jira_poll - INFO - Processing issue: AI-1234
2025-05-07 14:32:18 - jira_client - INFO - Downloaded attachment to ...
...
```

View live:

```bash
tail -f logs/*.log
```

## Extension Points

To add features:

1. **New Stage:** Create `stages/stage_N_*.py`
   - Implement function with clear in/out
   - Add logging
   - Call from `orchestrate.py`

2. **New API Integration:** Add to `utils/`
   - New client class
   - Error handling
   - Logging

3. **New Email Service:** Extend `stage_7_email.py`
   - Add `_send_via_service()` method
   - Update config

4. **Custom Build Agent:** Update `stage_2_build.py`
   - Integrate Claude API / aider
   - Parse requirements
   - Execute build

## Performance

Typical execution times:

- Stage 1 (Jira Poll): < 5 sec
- Stage 2 (Build): 5-30 min (external agent)
- Stage 3 (Tests): 1-5 min
- Stage 4 (GitHub): < 1 min
- Stage 5 (Vercel): 1-5 min
- Stage 6 (QA): 2-5 min
- Stage 7 (Email): < 1 sec
- Stage 8 (Jira Close): < 1 sec

**Total:** ~30-50 minutes per full pipeline run

## Security Considerations

- All credentials in `.env` (gitignored)
- API tokens not logged
- Output includes user code (be careful with sensitive data)
- Playwright runs in sandboxed browser context
- Email attachments are screenshots only (no source code)

## Monitoring & Debugging

### Check Pipeline Status

```bash
tail -f logs/*.log
```

### Manual Stage Execution

```bash
python -c "from stages.stage_1_jira_poll import stage_1_poll_jira; print(stage_1_poll_jira())"
```

### View Outputs

```bash
ls -la output/
cat output/AI-1234/test-results.txt
cat output/AI-1234/qa/bug-report.md
```

### Jira Integration Test

```bash
python -c "from utils.jira_client import JiraClient; j = JiraClient(); print(j.search_issues('project = YOUR_KEY'))"
```

## Next: Advanced

1. **Build Agent Integration:**
   - Integrate Claude Code / aider API
   - Parse requirements and generate code
   - Commit back to pipeline

2. **Notification Channels:**
   - Slack updates at each stage
   - WebSocket live dashboard
   - Webhook callbacks

3. **Multi-Project Support:**
   - Handle multiple Jira projects
   - Route to different templates

4. **Approval Gates:**
   - Manual review before deployment
   - Security scanning stage
   - Performance testing

5. **Deployment History:**
   - Database of all runs
   - Rollback capability
   - Performance metrics

---

**Version:** 1.0  
**Last Updated:** 2025-05-07
