# How to Check if Automation is Working

## Method 1: GitHub Actions Tab (Easiest)

1. **Go to your GitHub repository**
2. **Click "Actions" tab** (top of the page)
3. **Look for workflow runs:**
   - ✅ Green checkmark = Success
   - ❌ Red X = Failed
   - 🟡 Yellow circle = In progress
   - ⏰ Clock icon = Scheduled run

4. **Click on any run** to see:
   - When it started
   - How long it took
   - Detailed logs
   - What it did

**Example:**
```
✅ E-Play Contracts Scraper #5
   Scheduled workflow run
   2 hours ago
   Duration: 3m 45s
```

---

## Method 2: Check Google Sheets

1. **Open your Google Sheet**
2. **Look at the data:**
   - New contracts = It ran!
   - Updated timestamps = Fresh data
3. **Check last modified time** (bottom right of sheet)

---

## Method 3: GitHub Email Notifications

1. **Go to GitHub Settings:**
   - Click your profile → Settings
   - Notifications → Actions
2. **Enable:**
   - ✅ Workflow runs
   - ✅ Workflow run failures
3. **You'll get emails when:**
   - Workflow runs (optional)
   - Workflow fails (recommended)

---

## Method 4: Check Workflow Logs

1. **Go to Actions tab**
2. **Click on a workflow run**
3. **Click on "scrape" job**
4. **See logs like:**
   ```
   Starting E-Play scraper with cloudscraper...
   Initializing cloudscraper (solving Cloudflare challenge)...
   ✓ Session established
   Total pages: 75
   Page 1/75: 120 contracts (total: 120)
   Page 2/75: 120 contracts (total: 240)
   ...
   Total contracts found: 9000
   ✓ Uploaded to Google Sheets: https://...
   Done!
   ```

---

## What to Look For

### ✅ Success Indicators:
- Green checkmark in Actions tab
- "Done!" in logs
- New data in Google Sheets
- No error messages

### ❌ Failure Indicators:
- Red X in Actions tab
- Error messages in logs
- "ERROR" or "Failed" in logs
- No new data in Sheets

---

## Troubleshooting

### "I don't see any runs"
- **Check:** Is the schedule correct? (2 AM UTC)
- **Check:** Is the workflow file in `.github/workflows/`?
- **Check:** Is the repo public? (required for free Actions)

### "Runs are failing"
- **Check:** Logs for error messages
- **Check:** Secrets are set correctly
- **Check:** Google Sheets credentials are valid

### "I want to test it now"
- **Go to:** Actions → E-Play Contracts Scraper
- **Click:** "Run workflow" button (top right)
- **Select:** Branch (usually `main`)
- **Click:** Green "Run workflow" button

---

## Schedule Verification

To verify the schedule is set correctly:

1. **Check `.github/workflows/scraper.yml`:**
   ```yaml
   schedule:
     - cron: '0 2 * * *'  # Daily at 2 AM UTC
   ```

2. **Next scheduled run:**
   - GitHub shows "Next run" in Actions tab
   - Or calculate: 2 AM UTC = your local time

3. **Time conversion:**
   - 2 AM UTC = 9 PM EST (previous day)
   - 2 AM UTC = 3 AM CET
   - Use: https://www.timeanddate.com/worldclock/converter.html

---

## Quick Check Command

If you want to check programmatically, you can use GitHub API:

```bash
# Get latest workflow run status
curl https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/actions/runs?per_page=1
```

---

## Summary

**Easiest way:** Go to Actions tab → See green checkmarks = It's working! ✅

**Most reliable:** Check Google Sheets for new data

**Most detailed:** Click on a run → See full logs
