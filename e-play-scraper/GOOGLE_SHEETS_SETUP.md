# Google Sheets Setup Guide

## Quick Setup (5 minutes)

### Step 1: Create Google Cloud Project
1. Go to: https://console.cloud.google.com/
2. Click **"Select a project"** → **"New Project"**
3. Name it (e.g., "E-Play Scraper") → **Create**

### Step 2: Enable APIs
1. Go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Sheets API"** → **Enable**
3. Search for **"Google Drive API"** → **Enable**

### Step 3: Create Service Account
1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"Service account"**
3. Name it (e.g., "sheets-uploader") → **Create and Continue**
4. Skip role assignment → **Continue** → **Done**

### Step 4: Download JSON Key
1. Click on your service account (the email you just created)
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Select **JSON** → **Create**
5. JSON file downloads automatically
6. **Save it as `credentials.json`** in the `e-play-scraper` folder

### Step 5: Create & Share Google Sheet
1. Go to: https://sheets.google.com/
2. Create a new spreadsheet
3. Name it: **"E-Play Contracts"** (or update `SHEETS_SPREADSHEET_NAME` in script)
4. Click **"Share"** button (top right)
5. **Copy the service account email** from the JSON file (looks like: `xxx@xxx.iam.gserviceaccount.com`)
6. Paste it in the share dialog → **Give "Editor" access** → **Send**

### Step 6: Configure Script
Edit `scrape_contracts_api.py`:
```python
UPLOAD_TO_SHEETS = True  # Enable upload
SHEETS_SPREADSHEET_NAME = 'E-Play Contracts'  # Your sheet name
SHEETS_WORKSHEET_NAME = 'Contracts'  # Tab name (optional)
```

### Step 7: Install Dependencies
```bash
pip install gspread google-auth
```

### Step 8: Run Scraper
```bash
python scrape_contracts_api.py
```

The scraper will automatically upload to Google Sheets after scraping!

---

## Alternative: Upload Existing Data

If you already have `contracts.json`, use the standalone uploader:

```bash
python upload_to_sheets_simple.py
```

---

## Troubleshooting

**"credentials.json not found"**
- Make sure the JSON file is in the same folder as the script
- Check the filename is exactly `credentials.json`

**"SpreadsheetNotFound"**
- Make sure you shared the sheet with the service account email
- Check the sheet name matches `SHEETS_SPREADSHEET_NAME`

**"Permission denied"**
- The service account needs "Editor" access to the sheet
- Re-share the sheet with the service account email

**"gspread not installed"**
```bash
pip install gspread google-auth
```
