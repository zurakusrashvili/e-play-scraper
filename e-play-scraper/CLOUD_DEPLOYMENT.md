# Cloud Deployment Guide

Deploy the E-Play scraper to run automatically in the cloud. Choose the best option for you:

## 🚀 Recommended Options

### 1. **GitHub Actions** (FREE, Easiest) ⭐
- ✅ Free for public repos
- ✅ No credit card needed
- ✅ Runs on schedule automatically
- ✅ Easy setup (5 minutes)

### 2. **Railway** (Easy, $5/month)
- ✅ Very easy deployment
- ✅ Free trial available
- ✅ Automatic deployments
- ✅ Built-in scheduler

### 3. **Render** (Free tier available)
- ✅ Free tier (with limitations)
- ✅ Easy setup
- ✅ Automatic HTTPS

### 4. **Google Cloud Functions** (Pay per use)
- ✅ Serverless (only pay when running)
- ✅ Free tier: 2M invocations/month
- ✅ Integrates with Google Sheets

---

## Option 1: GitHub Actions (Recommended)

### Setup Steps:

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

2. **Add Secrets to GitHub**
   - Go to: `Settings` → `Secrets and variables` → `Actions`
   - Add these secrets:
     - `CF_CLEARANCE` - Your Cloudflare clearance cookie
     - `GA_COOKIE` - Google Analytics cookie (optional)
     - `GA_ZH4G2KK1JY` - Google Analytics cookie (optional)
     - `UPLOAD_TO_SHEETS` - Set to `true` to enable
     - `SHEETS_CREDENTIALS_JSON` - Your Google service account JSON (as string)
     - `SHEETS_SPREADSHEET_NAME` - Your sheet name (e.g., "E-Play Contracts")
     - `SHEETS_WORKSHEET_NAME` - Tab name (e.g., "Contracts")

3. **Get Google Credentials JSON as String**
   ```bash
   # On Windows PowerShell:
   $json = Get-Content credentials.json -Raw
   $json | Set-Clipboard
   
   # Or convert to base64:
   $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
   [Convert]::ToBase64String($bytes) | Set-Clipboard
   ```
   Paste the result into `SHEETS_CREDENTIALS_JSON` secret.

4. **Workflow runs automatically**
   - Runs daily at 2 AM UTC
   - Or trigger manually: `Actions` → `Run workflow`

### Update Schedule:
Edit `.github/workflows/scraper.yml`:
```yaml
- cron: '0 2 * * *'  # Change time here (UTC)
```

---

## Option 2: Railway

### Setup Steps:

1. **Sign up**: https://railway.app

2. **Create new project** → `Deploy from GitHub repo`

3. **Add Environment Variables**:
   - `CF_CLEARANCE` - Your Cloudflare cookie
   - `GA_COOKIE` - (optional)
   - `GA_ZH4G2KK1JY` - (optional)
   - `UPLOAD_TO_SHEETS` - `true`
   - `SHEETS_CREDENTIALS_JSON` - Your Google credentials JSON (as string)
   - `SHEETS_SPREADSHEET_NAME` - Your sheet name
   - `SHEETS_WORKSHEET_NAME` - Tab name

4. **Deploy**
   - Railway auto-detects Python
   - Uses `scheduler.py` to run on schedule

5. **Cost**: ~$5/month for always-on service

---

## Option 3: Render

### Setup Steps:

1. **Sign up**: https://render.com

2. **Create new Web Service** → Connect GitHub repo

3. **Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python scheduler.py`
   - **Plan**: Free (or paid for better performance)

4. **Add Environment Variables** (same as Railway)

5. **Deploy**

---

## Option 4: Google Cloud Functions

### Setup Steps:

1. **Install Google Cloud SDK**
   ```bash
   # Download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Create function**:
   ```bash
   gcloud functions deploy eplay-scraper \
     --runtime python311 \
     --trigger-http \
     --entry-point main \
     --set-env-vars CF_CLEARANCE=YOUR_COOKIE,UPLOAD_TO_SHEETS=true
   ```

3. **Schedule with Cloud Scheduler**:
   ```bash
   gcloud scheduler jobs create http eplay-scraper-daily \
     --schedule="0 2 * * *" \
     --uri="YOUR_FUNCTION_URL" \
     --http-method=GET
   ```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `CF_CLEARANCE` | ✅ Yes | Cloudflare clearance cookie |
| `GA_COOKIE` | ❌ No | Google Analytics cookie |
| `GA_ZH4G2KK1JY` | ❌ No | Google Analytics cookie |
| `UPLOAD_TO_SHEETS` | ❌ No | Set to `true` to enable |
| `SHEETS_CREDENTIALS_JSON` | ⚠️ If upload enabled | Google service account JSON (as string) |
| `SHEETS_SPREADSHEET_NAME` | ⚠️ If upload enabled | Your Google Sheet name |
| `SHEETS_WORKSHEET_NAME` | ❌ No | Tab name (default: "Contracts") |

---

## Getting Cookies

1. Open https://e-play.pl/umowy/ in Chrome
2. Press F12 → `Application` tab → `Cookies`
3. Copy:
   - `cf_clearance` → `CF_CLEARANCE`
   - `_ga` → `GA_COOKIE`
   - `_ga_ZH4G2KK1JY` → `GA_ZH4G2KK1JY`

**Note**: Cookies expire! Update them in secrets when they stop working.

---

## Getting Google Credentials

1. Follow: `GOOGLE_SHEETS_SETUP.md`
2. Download `credentials.json`
3. Convert to string for environment variable:
   ```python
   import json
   with open('credentials.json') as f:
       print(json.dumps(json.load(f)))
   ```
4. Or use base64 (cloud_scraper.py supports both)

---

## Testing Locally

```bash
# Set environment variables
export CF_CLEARANCE="your_cookie"
export UPLOAD_TO_SHEETS="true"
export SHEETS_CREDENTIALS_JSON='{"type":"service_account",...}'

# Run
python cloud_scraper.py
```

---

## Troubleshooting

**"CF_CLEARANCE not set"**
- Make sure you added the secret/environment variable
- Check the variable name matches exactly

**"Google Sheets upload failed"**
- Verify `SHEETS_CREDENTIALS_JSON` is valid JSON string
- Check service account has access to the sheet
- Make sure sheet name matches exactly

**"Cookies expired"**
- Update `CF_CLEARANCE` in your platform's secrets
- Get fresh cookie from browser

---

## Cost Comparison

| Platform | Free Tier | Paid | Best For |
|----------|-----------|------|----------|
| GitHub Actions | ✅ Yes | Free | Personal projects |
| Railway | ❌ No | $5/mo | Easy deployment |
| Render | ✅ Limited | $7/mo | Free tier users |
| Google Cloud | ✅ 2M/month | Pay per use | Serverless |

---

## Recommendation

**Start with GitHub Actions** - it's free and works great for scheduled tasks!
