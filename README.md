# Zero Human Touch Pipeline

A fully automated, end-to-end software delivery pipeline that transforms Jira stories into deployed web applications without any human intervention.

## How It Works

```
Jira Story (with requirements.md)
    ↓
Stage 1: Poll Jira for ai-ready stories
    ↓
Stage 2: AI builds the web app
    ↓
Stage 3: Write & run unit tests (iterate until passing)
    ↓
Stage 4: Push to GitHub & create PR
    ↓
Stage 5: Deploy to Vercel & wait for live URL
    ↓
Stage 6: QA tests with Playwright
    ↓
Stage 7: Email bug report with screenshots
    ↓
Stage 8: Update Jira story to Done or Bug Reported
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- GitHub account with a repository
- Jira Cloud instance with project
- Vercel account
- Playwright browsers installed
- Email service (SendGrid, Resend, or SMTP)
- GitHub CLI (`gh`) installed

### Installation

1. **Clone or create the pipeline directory:**

   ```bash
   cd "Zero Human Touch Pipeline"
   cd pipeline
   ```

2. **Create Python virtual environment:**

   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers:**

   ```bash
   python -m playwright install
   ```

5. **Install Node dependencies (for any Node projects):**
   ```bash
   npm install
   npx playwright install  # For JavaScript/Playwright tests
   ```

### Configuration

1. **Copy environment template:**

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials:**

   ```env
   # Jira
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_USERNAME=your-email@example.com
   JIRA_API_TOKEN=<get-from-https://id.atlassian.com/manage/api-tokens>
   JIRA_PROJECT_KEY=YOUR_PROJECT_KEY

   # GitHub
   GITHUB_TOKEN=<github-personal-access-token>
   GITHUB_REPO_OWNER=your-username
   GITHUB_REPO_NAME=your-repo-name

   # Vercel
   VERCEL_TOKEN=<vercel-api-token>

   # Email (choose one service)
   EMAIL_SERVICE=sendgrid
   SENDGRID_API_KEY=<your-key>
   EMAIL_FROM=pipeline@example.com
   EMAIL_TO=qa-reports@example.com

   # Claude/AI
   ANTHROPIC_API_KEY=<your-key>
   ```

3. **Authenticate with GitHub CLI:**
   ```bash
   gh auth login
   ```

### Running the Pipeline

#### Option 1: Run Once (Manual)

```bash
python orchestrate.py
```

#### Option 2: Run on Schedule (Cron)

```bash
python scheduler.py
```

This will poll Jira every 5 minutes (configurable in `.env` via `CRON_INTERVAL`).

#### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Repeat every 5 minutes
4. Set action:
   ```
   Program: C:\path\to\venv\Scripts\python.exe
   Arguments: C:\path\to\pipeline\scheduler.py
   Start in: C:\path\to\pipeline
   ```

#### Option 4: Linux/Mac Cron

```bash
# Edit crontab
crontab -e

# Add line (runs every 5 minutes)
*/5 * * * * cd /path/to/pipeline && /path/to/venv/bin/python scheduler.py >> /tmp/pipeline.log 2>&1
```

## Creating a Jira Story to Test

1. **Create a new story in your Jira project:**
   - **Title:** `[AI-PIPELINE] <short description>`
   - **Label:** `ai-ready`
   - **Status:** To Do

2. **Create a `requirements.md` file:**

   ```markdown
   # Requirements — Simple Todo App

   ## What to build

   A single-page web application that lets a user manage a todo list.

   ## Features

   - Add a new todo item via a text input and a button
   - Mark a todo as complete (strikethrough + visual indicator)
   - Delete a todo item
   - Show a count of remaining incomplete items
   - Persist todos in localStorage

   ## Tech

   - Plain HTML, CSS, JavaScript — no framework
   - Single file output preferred (index.html)
   - Must work in Chrome without any build step

   ## Acceptance criteria

   - All 5 features work correctly
   - No console errors
   - Page is usable on mobile (375px wide)
   ```

3. **Attach `requirements.md` to the Jira story**

4. **Step away from keyboard** - the pipeline will handle everything!

## Pipeline Stages Explained

### Stage 1: Jira Polling

- Queries Jira for stories with `ai-ready` label in `To Do` status
- Downloads `requirements.md` attachment
- Transitions story to `In Progress`

### Stage 2: Build

- External agent (Claude Code, aider, Cursor) reads requirements
- Builds working web app in output directory
- Follows specified tech stack

### Stage 3: Unit Tests

- Detects test framework (Jest, pytest, etc.)
- Writes meaningful unit tests
- Runs tests in loop until all pass
- Saves results to `test-results.txt`

### Stage 4: GitHub

- Initializes git repo
- Creates feature branch: `feature/ISSUE-KEY-description`
- Commits and pushes code
- Opens Pull Request with Jira key in title

### Stage 5: Vercel Deployment

- Triggers Vercel deployment from branch
- Polls deployment status every 10 seconds
- Waits for `READY` state (max 5 minutes)
- Performs health check on live URL

### Stage 6: QA Testing

- Opens deployed URL in Playwright browser
- Tests each acceptance criterion
- Captures console errors
- Takes screenshots of key states
- Generates bug report in Markdown

### Stage 7: Email Report

- Sends QA report to configured email
- Attaches all screenshots
- Includes pass/fail status and details

### Stage 8: Jira Close

- Transitions story to `Done` (if all tests pass)
- Transitions to `Bug Reported` (if failures found)
- Adds comment with deployment URL and summary

## Logs

Pipeline logs are written to:

- `logs/YYYYMMDD.log` - Detailed logs with timestamps

View live logs:

```bash
tail -f logs/*.log
```

## Output Structure

```
output/
├── AI-1234/                          # Jira issue key
│   ├── index.html                    # Built app files
│   ├── app.js
│   ├── style.css
│   ├── test-results.txt             # Test output
│   ├── qa/
│   │   ├── bug-report.md            # QA findings
│   │   ├── screenshot-01-initial.png
│   │   └── screenshot-02-tests.png
```

## Error Handling

The pipeline handles failures gracefully:

- **Build fails:** Story moved to `Bug Reported`, Jira comment added
- **Tests fail:** Loop continues, agent fixes code, retries tests
- **Deployment fails:** Story moved to `Bug Reported`
- **QA fails:** Report generated, email sent, story remains in appropriate state
- **Any stage fails:** Jira updated with error message, pipeline stops

**No silent failures.** Every failure is logged and Jira is updated.

## Architecture

### Files

- `orchestrate.py` - Main pipeline orchestrator
- `scheduler.py` - Cron job runner
- `stages/stage_*.py` - Individual pipeline stages
- `utils/` - Configuration, logging, API clients

### Key Configuration

- `utils/config.py` - Load from `.env`
- `utils/logger.py` - Logging setup
- `utils/jira_client.py` - Jira API integration

## API Integrations

### Jira REST API v3

- Search issues with JQL
- Download attachments
- Transition issues
- Add comments

### GitHub API

- Create branches and commits
- Push to remote
- Open pull requests

### Vercel API

- Trigger deployments
- Poll deployment status
- Extract live URLs

### Playwright API

- Browser automation
- Screenshot capture
- Console error capture
- DOM interaction

### Email Services

- **SendGrid:** REST API
- **Resend:** REST API
- **SMTP:** Standard email protocol

## Testing the Pipeline

### Quick Test (5 minutes)

1. Create a Jira story with simple requirements
2. Run: `python orchestrate.py`
3. Watch each stage complete
4. Check Jira for final status

### Full Test with Scheduler

1. Run: `python scheduler.py`
2. Leave running
3. Create Jira stories on schedule
4. Pipeline automatically processes them

### Debug Mode

View detailed logs during execution:

```bash
tail -f logs/*.log &
python orchestrate.py
```

## Troubleshooting

### Jira API errors

- Verify API token is valid at https://id.atlassian.com/manage/api-tokens
- Verify project key is correct
- Check user has access to project

### GitHub push fails

- Run: `gh auth login`
- Verify token has `repo` and `workflow` permissions
- Verify repository exists and you have push access

### Vercel deployment fails

- Verify Vercel API token is valid
- Ensure repository is connected to Vercel
- Check GitHub workflow runs successfully

### Playwright tests fail

- Ensure browsers are installed: `python -m playwright install`
- Check Firefox/Chromium/WebKit available in your OS

### Email not received

- Verify email configuration is correct
- Check spam folder
- Verify API keys have correct permissions

## Contributing

To extend the pipeline:

1. Create new stage in `stages/stage_N_*.py`
2. Import and call in `orchestrate.py`
3. Add error handling
4. Log progress with `logger.info()`
5. Return structured result dict

## Support

For issues or questions:

1. Check logs in `logs/` directory
2. Review pipeline status in Jira
3. Verify all API credentials in `.env`
4. Run manual test: `python orchestrate.py`

## Next Steps

1. Set up `.env` with your credentials
2. Create a test Jira story
3. Run the pipeline manually: `python orchestrate.py`
4. Once working, set up scheduler for continuous operation
5. Record Loom video showing full end-to-end flow
6. Submit for review

---

**Deadline:** 18th May
**Submit:** Loom recording + GitHub repo link
#   Z e r o - H u m a n - T o u c h - P i p e l i n e  
 