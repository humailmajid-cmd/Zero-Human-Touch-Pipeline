# Zero Human Touch Pipeline

An end-to-end automated software delivery pipeline that takes a Jira story from **To Do** to a live, QA-verified deployment — with zero human intervention.

---

## What It Does

The pipeline polls Jira on a configurable schedule and, when it finds a new story, automatically:

1. **Picks up the Jira story** — transitions it to In Progress and claims it so no duplicate runs occur
2. **Builds the web application** — hands the requirements to an AI build agent (Claude) that generates the full codebase
3. **Runs unit tests** — detects the project type (Node.js or Python) and runs the appropriate test suite
4. **Pushes to GitHub** — initialises a git repo, creates a feature branch, commits the build, and opens a Pull Request via the GitHub API
5. **Deploys to Vercel** — uploads the built files, triggers a deployment, polls until live, and runs a health check
6. **Runs QA with Playwright** — navigates the live deployment, tests acceptance criteria extracted from the Jira story, captures screenshots, and generates a bug report
7. **Sends an email report** — delivers the QA results and screenshots via SendGrid, Resend, or SMTP
8. **Closes the Jira story** — transitions it to Done (or Bug Reported on failure) and posts a full summary comment

---

## Pipeline Flow

```
Jira Story (To Do)
        ↓
Stage 1: Poll Jira → claim story, extract requirements
        ↓
Stage 2: AI builds the web app
        ↓
Stage 3: Run unit tests
        ↓
Stage 4: Push to GitHub → open Pull Request
        ↓
Stage 5: Deploy to Vercel → wait for live URL
        ↓
Stage 6: Playwright QA → test acceptance criteria, screenshots
        ↓
Stage 7: Email QA report with attachments
        ↓
Stage 8: Close Jira story → Done or Bug Reported
```

---

## Project Structure

```
pipeline/
├── orchestrate.py          ← Pipeline coordinator
├── scheduler.py            ← Cron runner
├── stages/
│   ├── stage_1_jira_poll.py
│   ├── stage_2_build.py
│   ├── stage_3_tests.py
│   ├── stage_4_github.py
│   ├── stage_5_vercel.py
│   ├── stage_6_qa.py
│   ├── stage_7_email.py
│   └── stage_8_jira_close.py
└── utils/
    ├── jira_client.py      ← Jira REST API v3 wrapper
    ├── config.py           ← Environment config loader
    └── logger.py           ← Structured logger
```

Output for each processed story is written to:

```
output/
└── AP-2/
    ├── (built app files)
    ├── test-results.txt
    └── qa/
        ├── bug-report.md
        ├── screenshot-01-initial-load.png
        └── screenshot-02-after-tests.png
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/humailmajid-cmd/Zero-Human-Touch-Pipeline.git
cd Zero-Human-Touch-Pipeline/pipeline
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure environment

```bash
cp .env.example .env
```

Fill in `.env` — see the table below.

### 4. Run

```bash
# Run once immediately
python orchestrate.py

# Or run on a schedule (polls every CRON_INTERVAL minutes)
python scheduler.py
```

---

## Configuration

| Variable | Description |
|---|---|
| `JIRA_URL` | Base URL of your Atlassian instance — e.g. `https://your-org.atlassian.net` |
| `JIRA_USERNAME` | Your Atlassian account email |
| `JIRA_API_TOKEN` | API token from id.atlassian.com/manage-profile/security/api-tokens |
| `JIRA_PROJECT_KEY` | Project key to poll — e.g. `AP` |
| `GITHUB_TOKEN` | Personal access token with `repo` scope |
| `GITHUB_REPO_OWNER` | GitHub username or organisation |
| `GITHUB_REPO_NAME` | Target repository name |
| `VERCEL_TOKEN` | Token from vercel.com → Settings → Tokens |
| `VERCEL_TEAM_ID` | Team slug — leave blank for personal accounts |
| `EMAIL_SERVICE` | `sendgrid`, `resend`, or `smtp` |
| `SENDGRID_API_KEY` | SendGrid API key (if using SendGrid) |
| `RESEND_API_KEY` | Resend API key (if using Resend) |
| `SMTP_HOST / PORT / USER / PASSWORD` | SMTP credentials (if using smtp) |
| `EMAIL_FROM` | Sender address |
| `EMAIL_TO` | Recipient for QA reports |
| `ANTHROPIC_API_KEY` | Claude API key for the AI build agent |
| `CRON_INTERVAL` | How often to poll Jira in minutes (default: `5`) |

---

## How Stories Are Picked Up

The pipeline queries Jira for issues in **"To Do"** status, ordered by creation date (oldest first). The moment it finds one it transitions it to **"In Progress"**, so concurrent scheduler runs never process the same story twice.

On success → **Done** with a deployment URL comment.
On failure → **Bug Reported** with the error details.

---

## API Integrations

- **Jira REST API v3** — search, transition, comment
- **GitHub REST API** — branches, commits, pull requests (no CLI dependency)
- **Vercel API** — deployments, status polling
- **Playwright** — browser automation, screenshots, console capture
- **SendGrid / Resend / SMTP** — QA report email delivery

---

## Requirements

- Python 3.10+
- Git on PATH
- A Jira Cloud project with stories in "To Do"
- A GitHub repository for the generated code
- A Vercel account for deployment
- An email provider (SendGrid / Resend / SMTP)
