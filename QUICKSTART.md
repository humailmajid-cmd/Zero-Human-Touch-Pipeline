# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies

```bash
cd pipeline
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
python -m playwright install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
nano .env
```

Required credentials:

- **Jira:** API token from https://id.atlassian.com/manage/api-tokens
- **GitHub:** Personal access token with `repo` + `workflow` scopes
- **Vercel:** API token from https://vercel.com/account/tokens
- **Email:** SendGrid API key (or SMTP credentials)

### 3. Test Manually

```bash
python orchestrate.py
```

You should see:

- Stage 1: Poll Jira for ai-ready stories
- If story found: Proceed through all 8 stages
- If no story: "No new ai-ready stories found"

### 4. Start Scheduler

```bash
python scheduler.py
```

This runs every 5 minutes. Leave it running in a terminal.

### 5. Create Test Story

1. Go to your Jira project
2. Create story with:
   - Title: `[AI-PIPELINE] Test Todo App`
   - Label: `ai-ready`
   - Status: `To Do`
   - Attachment: `requirements.md`

3. Wait up to 5 minutes for pipeline to pick it up
4. Watch logs: `tail -f logs/*.log`

## Verifying Each Stage

### After Stage 1 (Jira Poll)

- Story should be `In Progress`
- `logs/` should have new entries
- `output/AI-XXXX/` directory created

### After Stage 2 (Build)

- Requires external agent to build
- `output/AI-XXXX/BUILD_INSTRUCTIONS.md` created
- (Manual: Use Claude Code / aider to build app)

### After Stage 3 (Tests)

- `output/AI-XXXX/test-results.txt` created
- Tests should pass

### After Stage 4 (GitHub)

- New branch created: `feature/AI-XXXX-...`
- PR opened on GitHub

### After Stage 5 (Vercel)

- Live deployment URL generated
- URL passes health check

### After Stage 6 (QA)

- `output/AI-XXXX/qa/bug-report.md` created
- Screenshots saved

### After Stage 7 (Email)

- Email received at EMAIL_TO address
- Includes bug report + screenshots

### After Stage 8 (Jira Close)

- Story transitioned to `Done` or `Bug Reported`
- Comment added with deployment URL

## Troubleshooting

### "No module named utils"

```bash
# Make sure you're in the pipeline directory
cd pipeline
python orchestrate.py
```

### "JIRA API error"

- Check `.env` has correct JIRA_URL and credentials
- Verify API token at https://id.atlassian.com/manage/api-tokens

### "gh: command not found"

- Install GitHub CLI: https://cli.github.com
- Run: `gh auth login`

### "playwright: command not found"

```bash
python -m playwright install
```

### Tests not running

- Ensure app has test files (package.json with test script)
- Or let external agent create tests

## Recording for Submission

Record a Loom video showing:

1. Create Jira story
2. Step away
3. Show scheduler running
4. Show each stage completing
5. Show live deployment
6. Show Playwright testing
7. Show email received
8. Show Jira in Done state

```bash
# In one terminal:
python scheduler.py

# In another terminal:
tail -f logs/*.log
```

Create Jira story → wait 5 minutes → all done!

## Common Issues

| Issue                                 | Solution                                                         |
| ------------------------------------- | ---------------------------------------------------------------- |
| `requests.exceptions.ConnectionError` | Check JIRA_URL is correct and accessible                         |
| `github.GithubException`              | Verify GITHUB_TOKEN has repo permissions                         |
| `playwright timeout`                  | Playwright browser not installed: `python -m playwright install` |
| `FileNotFoundError: requirements.md`  | Ensure attachment is exactly named `requirements.md`             |
| Email not received                    | Check EMAIL_SERVICE, API key, and EMAIL_TO address               |

## Key Concepts

- **Poll frequency:** Set `CRON_INTERVAL` in `.env` (default 5 min)
- **Output directory:** Check `output/` for builds, tests, QA reports
- **Logs:** Always in `logs/YYYYMMDD.log`
- **Failure handling:** Every failure updates Jira automatically
- **No human touch:** Everything automatic after story creation

## Next: Advanced

- Extend build agent to use Claude API
- Add custom test templates
- Integrate with Slack notifications
- Add deployment approval gates
- Multi-project support
