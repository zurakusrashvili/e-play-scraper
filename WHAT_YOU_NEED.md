# What You Need for GitHub Actions

## 📋 Quick Summary

You need **3 things** to set up GitHub Actions:

1. **GitHub Repository** (5 min)
2. **Cookies from Browser** (2 min) 
3. **Google Credentials** (10 min - only if uploading to Sheets)

---

## 1️⃣ GitHub Repository

**What:** Push your code to GitHub

**Steps:**
```bash
# In your project folder (C:\Users\admin\bacho)
git init
git add .
git commit -m "Add E-Play scraper with GitHub Actions"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

**Important:** Repository must be **PUBLIC** for free GitHub Actions!

---

## 2️⃣ Cookies (REQUIRED)

**What:** Get `cf_clearance` cookie from your browser

**Steps:**
1. Open Chrome
2. Go to: https://e-play.pl/umowy/
3. Press `F12` → `Application` tab → `Cookies` → `https://e-play.pl`
4. Find `cf_clearance` → Copy the **Value** (long string)
5. Save it - you'll paste it in GitHub Secrets

**You'll need:**
- `CF_CLEARANCE` = the cookie value you copied

**Note:** This cookie expires! Update it in GitHub Secrets when scraper stops working.

---

## 3️⃣ Google Credentials (Only if Uploading to Sheets)

**What:** Service account JSON for Google Sheets access

**Steps:**
1. Go to: https://console.cloud.google.com/
2. Create project → Enable "Google Sheets API" and "Google Drive API"
3. Create Service Account → Download JSON key
4. Share your Google Sheet with the service account email
5. Run: `python e-play-scraper/convert_credentials.py`
6. Copy the output string

**You'll need:**
- `SHEETS_CREDENTIALS_JSON` = the JSON string from step 5
- `SHEETS_SPREADSHEET_NAME` = your sheet name (e.g., "E-Play Contracts")
- `UPLOAD_TO_SHEETS` = `true`

**Detailed guide:** See `e-play-scraper/GOOGLE_SHEETS_SETUP.md`

---

## 🎯 Next Steps

1. **Read the full guide:** `e-play-scraper/GITHUB_ACTIONS_SETUP.md`
2. **Or use quick checklist:** `GITHUB_SETUP_CHECKLIST.md`

---

## ⚡ Quick Start (If You're Ready)

1. **Get cookies** (Step 2 above)
2. **Get Google credentials** (Step 3 above - if using Sheets)
3. **Push to GitHub** (Step 1 above)
4. **Add secrets:**
   - Go to: Repo → Settings → Secrets → Actions
   - Add: `CF_CLEARANCE`, `UPLOAD_TO_SHEETS`, `SHEETS_CREDENTIALS_JSON`, etc.
5. **Test:** Actions tab → Run workflow

**That's it!** 🚀
