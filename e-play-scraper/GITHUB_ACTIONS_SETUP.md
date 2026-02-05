# GitHub Actions Setup - Step by Step

## What You'll Need

1. ✅ GitHub account (free)
2. ✅ Cookies from e-play.pl (cf_clearance)
3. ✅ Google Sheets credentials (if uploading to Sheets)

---

## Step 1: Push Code to GitHub

### Option A: New Repository

1. **Create new repo on GitHub**
   - Go to: https://github.com/new
   - Name it: `e-play-scraper` (or any name)
   - Make it **Public** (required for free GitHub Actions)
   - Click **Create repository**

2. **Push your code:**
   ```bash
   cd C:\Users\admin\bacho
   git init
   git add .
   git commit -m "Initial commit - E-Play scraper"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/e-play-scraper.git
   git push -u origin main
   ```

### Option B: Existing Repository

```bash
cd C:\Users\admin\bacho
git add .
git commit -m "Add GitHub Actions workflow"
git push
```

---

## Step 2: Get Cookies from Browser

1. **Open Chrome** and go to: https://e-play.pl/umowy/

2. **Open DevTools:**
   - Press `F12` or `Right-click` → `Inspect`

3. **Get Cookies:**
   - Go to `Application` tab (top)
   - In left sidebar: `Storage` → `Cookies` → `https://e-play.pl`
   - Find these cookies and copy their **Value**:

   | Cookie Name | Copy This Value |
   |-------------|----------------|
   | `cf_clearance` | **REQUIRED** - Copy the long value |
   | `_ga` | Optional - Copy if exists |
   | `_ga_ZH4G2KK1JY` | Optional - Copy if exists |

4. **Save them somewhere** - you'll need them in Step 4

**Note**: `cf_clearance` expires! You'll need to update it when it stops working (usually every few days/weeks).

---

## Step 3: Get Google Sheets Credentials (If Uploading to Sheets)

### 3.1: Create Service Account

1. **Go to Google Cloud Console:**
   - https://console.cloud.google.com/

2. **Create/Select Project:**
   - Click project dropdown → `New Project`
   - Name: `E-Play Scraper` → `Create`

3. **Enable APIs:**
   - Go to: `APIs & Services` → `Library`
   - Search: `Google Sheets API` → `Enable`
   - Search: `Google Drive API` → `Enable`

4. **Create Service Account:**
   - Go to: `APIs & Services` → `Credentials`
   - Click: `+ CREATE CREDENTIALS` → `Service account`
   - Name: `sheets-uploader` → `Create and Continue`
   - Skip role → `Continue` → `Done`

5. **Download JSON Key:**
   - Click on your service account (the email)
   - Go to `Keys` tab
   - Click `Add Key` → `Create new key`
   - Select `JSON` → `Create`
   - File downloads automatically

### 3.2: Share Google Sheet

1. **Create/Open your Google Sheet:**
   - Go to: https://sheets.google.com
   - Create new sheet or open existing
   - Name it: `E-Play Contracts` (or your preferred name)

2. **Share with Service Account:**
   - Click `Share` button (top right)
   - **Copy the service account email** from the JSON file you downloaded
     - Look for: `"client_email": "xxx@xxx.iam.gserviceaccount.com"`
   - Paste email in share dialog
   - Give `Editor` access → `Send`

### 3.3: Convert JSON to String

1. **Save the JSON file** as `credentials.json` in your project folder

2. **Convert to string** (choose one method):

   **Method 1: Python Script** (Easiest)
   ```bash
   python convert_credentials.py
   ```
   This will copy the JSON string to your clipboard!

   **Method 2: Manual**
   ```python
   import json
   with open('credentials.json', 'r') as f:
       json_str = json.dumps(json.load(f))
       print(json_str)
   ```
   Copy the entire output (it's one long line)

   **Method 3: PowerShell** (Windows)
   ```powershell
   $json = Get-Content credentials.json -Raw
   $json | Set-Clipboard
   ```
   Now paste it (Ctrl+V) - it's already in your clipboard!

---

## Step 4: Add Secrets to GitHub

1. **Go to your GitHub repository**

2. **Navigate to Secrets:**
   - Click `Settings` tab (top of repo)
   - In left sidebar: `Secrets and variables` → `Actions`
   - Click `New repository secret`

3. **Choose your setup:**

   ### Option A: Automated Cookie Refresh (Recommended - No Manual Updates!)
   
   If you want cookies to refresh automatically (so you never have to update them):
   
   | Secret Name | Value | Required? |
   |-------------|-------|-----------|
   | `AUTO_REFRESH_COOKIES` | Type: `true` | ✅ **YES** (for auto-refresh) |
   | `CF_CLEARANCE` | Paste cookie from Step 2 (optional fallback) | ❌ No (but recommended as backup) |
   | `UPLOAD_TO_SHEETS` | Type: `true` (if using Sheets) | ⚠️ If using Sheets |
   | `SHEETS_CREDENTIALS_JSON` | Paste JSON string from Step 3.3 | ⚠️ If using Sheets |
   | `SHEETS_SPREADSHEET_NAME` | Type: `E-Play Contracts` | ⚠️ If using Sheets |
   | `SHEETS_WORKSHEET_NAME` | Type: `Contracts` | ❌ No |
   
   **With this setup:** Cookies refresh automatically! You never need to update `CF_CLEARANCE` manually.
   
   ### Option B: Manual Cookies (Update When They Expire)
   
   If you prefer to manage cookies manually:
   
   | Secret Name | Value | Required? |
   |-------------|-------|-----------|
   | `CF_CLEARANCE` | Paste the `cf_clearance` cookie value from Step 2 | ✅ **YES** |
   | `GA_COOKIE` | Paste the `_ga` cookie value (optional) | ❌ No |
   | `GA_ZH4G2KK1JY` | Paste the `_ga_ZH4G2KK1JY` cookie value (optional) | ❌ No |
   | `UPLOAD_TO_SHEETS` | Type: `true` (if using Sheets) | ⚠️ If using Sheets |
   | `SHEETS_CREDENTIALS_JSON` | Paste JSON string from Step 3.3 | ⚠️ If using Sheets |
   | `SHEETS_SPREADSHEET_NAME` | Type: `E-Play Contracts` | ⚠️ If using Sheets |
   | `SHEETS_WORKSHEET_NAME` | Type: `Contracts` | ❌ No |
   
   **With this setup:** You'll need to update `CF_CLEARANCE` manually when it expires.

4. **Click `Add secret`** for each one

---

## Step 5: Test the Workflow

1. **Go to Actions tab** in your GitHub repo

2. **Run manually:**
   - Click `E-Play Contracts Scraper` workflow (left sidebar)
   - Click `Run workflow` button (right side)
   - Select branch: `main`
   - Click green `Run workflow` button

3. **Watch it run:**
   - Click on the running workflow
   - Click on `scrape` job
   - Watch the logs in real-time!

4. **Check results:**
   - If using Sheets: Check your Google Sheet - data should appear!
   - Check workflow logs for any errors

---

## Step 6: Verify Schedule

The workflow runs **automatically daily at 2 AM UTC**.

To change the schedule, edit `.github/workflows/scraper.yml`:
```yaml
- cron: '0 2 * * *'  # Change this line
```

**Cron format:** `minute hour day month day-of-week`
- `0 2 * * *` = 2 AM UTC daily
- `0 14 * * *` = 2 PM UTC daily
- `0 */6 * * *` = Every 6 hours

---

## Troubleshooting

### ❌ "CF_CLEARANCE not set"
- Make sure you added the secret with exact name: `CF_CLEARANCE`
- Check it's not empty

### ❌ "Cookies expired" / "403 Forbidden"
- Cookies expire! Get fresh cookies from browser (Step 2)
- Update `CF_CLEARANCE` secret with new value

### ❌ "Google Sheets upload failed"
- Check `SHEETS_CREDENTIALS_JSON` is valid JSON (one long string)
- Verify service account email has access to the sheet
- Check `SHEETS_SPREADSHEET_NAME` matches exactly

### ❌ "Workflow not running"
- Make sure repo is **Public** (free tier requirement)
- Check workflow file is in: `.github/workflows/scraper.yml`
- Verify you committed and pushed the file

### ❌ "Module not found"
- Check workflow installs dependencies correctly
- Look at the "Install dependencies" step in logs

---

## Updating Cookies (When They Expire)

1. Get fresh cookies from browser (Step 2)
2. Go to: `Settings` → `Secrets and variables` → `Actions`
3. Click on `CF_CLEARANCE` secret
4. Click `Update` → Paste new value → `Update secret`
5. Done! Next run will use new cookies

---

## Summary Checklist

- [ ] Code pushed to GitHub
- [ ] Got `cf_clearance` cookie from browser
- [ ] Created Google service account (if using Sheets)
- [ ] Shared Google Sheet with service account
- [ ] Converted credentials.json to string
- [ ] Added all secrets to GitHub
- [ ] Tested workflow manually
- [ ] Verified schedule is correct

---

## Next Steps

Once set up:
- ✅ Runs automatically daily at 2 AM UTC
- ✅ Uploads to Google Sheets (if enabled)
- ✅ You can trigger manually anytime from Actions tab
- ✅ Check logs if something goes wrong

**That's it! Your scraper is now running in the cloud! 🚀**
