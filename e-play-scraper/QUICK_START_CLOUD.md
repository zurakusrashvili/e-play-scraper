# Quick Start: Deploy to Cloud (5 minutes)

## 🎯 GitHub Actions (Recommended - FREE)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Add scraper"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### Step 2: Add Secrets
Go to: `Your Repo` → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Add these secrets:

| Secret Name | Value |
|------------|-------|
| `CF_CLEARANCE` | Your Cloudflare cookie (from browser) |
| `UPLOAD_TO_SHEETS` | `true` |
| `SHEETS_CREDENTIALS_JSON` | Your Google credentials JSON (see below) |
| `SHEETS_SPREADSHEET_NAME` | `E-Play Contracts` |

### Step 3: Get Google Credentials
1. Follow `GOOGLE_SHEETS_SETUP.md` to create service account
2. Download `credentials.json`
3. Convert to string:
   ```python
   import json
   with open('credentials.json') as f:
       print(json.dumps(json.load(f)))
   ```
4. Copy the output → Paste into `SHEETS_CREDENTIALS_JSON` secret

### Step 4: Done! 
- Runs automatically daily at 2 AM UTC
- Or trigger manually: `Actions` tab → `Run workflow`

---

## 🚂 Railway (Alternative)

1. Sign up: https://railway.app
2. New Project → Deploy from GitHub
3. Add environment variables (same as GitHub secrets above)
4. Deploy!

---

## 📝 Getting Cookies

1. Open https://e-play.pl/umowy/ in Chrome
2. F12 → `Application` → `Cookies` → `https://e-play.pl`
3. Copy `cf_clearance` value → Use for `CF_CLEARANCE` secret

**Note**: Cookies expire! Update when scraper stops working.

---

## ❓ Need Help?

See full guide: `CLOUD_DEPLOYMENT.md`
