# GitHub Actions Setup - Quick Checklist

## ✅ Step-by-Step Checklist

### 1. Prepare Your Code
- [ ] Make sure `.github/workflows/scraper.yml` exists in your repo root
- [ ] Make sure `e-play-scraper/cloud_scraper.py` exists
- [ ] Commit and push to GitHub

### 2. Get Cookies (Required)
- [ ] Open https://e-play.pl/umowy/ in Chrome
- [ ] Press F12 → Application tab → Cookies
- [ ] Copy `cf_clearance` value
- [ ] (Optional) Copy `_ga` and `_ga_ZH4G2KK1JY` values

### 3. Get Google Credentials (If Using Sheets)
- [ ] Create Google Cloud project
- [ ] Enable Sheets API & Drive API
- [ ] Create service account
- [ ] Download credentials.json
- [ ] Share Google Sheet with service account email
- [ ] Run: `python e-play-scraper/convert_credentials.py`
- [ ] Copy the JSON string output

### 4. Add GitHub Secrets
Go to: Your Repo → Settings → Secrets and variables → Actions

- [ ] `CF_CLEARANCE` = your cf_clearance cookie
- [ ] `GA_COOKIE` = your _ga cookie (optional)
- [ ] `GA_ZH4G2KK1JY` = your _ga_ZH4G2KK1JY cookie (optional)
- [ ] `UPLOAD_TO_SHEETS` = `true` (if using Sheets)
- [ ] `SHEETS_CREDENTIALS_JSON` = JSON string from step 3
- [ ] `SHEETS_SPREADSHEET_NAME` = `E-Play Contracts` (or your name)
- [ ] `SHEETS_WORKSHEET_NAME` = `Contracts` (optional)

### 5. Test It
- [ ] Go to Actions tab
- [ ] Click "Run workflow" → Run
- [ ] Watch it execute
- [ ] Check Google Sheet (if enabled)

### 6. Done! 🎉
- [ ] Workflow runs daily at 2 AM UTC automatically
- [ ] You can trigger manually anytime

---

## 📝 Important Notes

- **Repository must be PUBLIC** for free GitHub Actions
- **Cookies expire** - update `CF_CLEARANCE` when scraper stops working
- **Schedule**: Runs daily at 2 AM UTC (edit `.github/workflows/scraper.yml` to change)

---

## 🆘 Need Help?

See detailed guide: `e-play-scraper/GITHUB_ACTIONS_SETUP.md`
