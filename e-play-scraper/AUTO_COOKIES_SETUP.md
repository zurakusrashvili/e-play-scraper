# Automated Cookie Refresh Setup

## Overview

This setup automatically refreshes cookies before scraping, so you don't need to manually update them when they expire!

## How It Works

1. **Before scraping**: Runs a headless browser to get fresh cookies
2. **Tests cookies**: Validates they work before using them
3. **Auto-refresh on failure**: If cookies expire during scraping, automatically refreshes them
4. **Falls back gracefully**: If auto-refresh fails, uses environment variables

## Setup for GitHub Actions

### Option 1: Full Automation (Recommended)

1. **Add one more secret to GitHub:**
   - Go to: Repo → Settings → Secrets → Actions
   - Add: `AUTO_REFRESH_COOKIES` = `true`

2. **That's it!** The workflow will:
   - Install Playwright
   - Get fresh cookies automatically
   - Use them for scraping

### Option 2: Manual Cookies (Current Method)

- Don't add `AUTO_REFRESH_COOKIES` secret, or set it to `false`
- Manually update `CF_CLEARANCE` when cookies expire

## How It Works in GitHub Actions

The workflow now:
1. Installs Playwright and Chromium
2. Runs `get_cookies_automated.py` to get fresh cookies
3. Uses `cloud_scraper_auto_cookies.py` which:
   - Tests cookies before scraping
   - Auto-refreshes if they fail
   - Falls back to env vars if refresh fails

## Local Testing

### Test Cookie Refresh

```bash
cd e-play-scraper
pip install playwright
playwright install chromium
python get_cookies_automated.py
```

### Test Full Scraper with Auto-Cookies

```bash
# Set environment variables (optional - will auto-refresh if not set)
export AUTO_REFRESH_COOKIES=true
python cloud_scraper_auto_cookies.py
```

## Benefits

✅ **No manual cookie updates** - Cookies refresh automatically  
✅ **Handles Cloudflare challenges** - Playwright solves them  
✅ **Graceful fallback** - Uses env vars if auto-refresh fails  
✅ **Tests cookies** - Validates before use  
✅ **Auto-retry** - Refreshes if cookies expire during scraping  

## Troubleshooting

### "Playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### "Cookie refresh failed"
- Check internet connection
- Cloudflare might be blocking - wait a few minutes and retry
- Falls back to environment variables automatically

### "Cookies still not working"
- Set `AUTO_REFRESH_COOKIES=false` to use manual cookies
- Update `CF_CLEARANCE` secret manually

## Cost

- **GitHub Actions**: Free (runs in GitHub's infrastructure)
- **Playwright**: Free (open source)
- **Time**: Adds ~10-15 seconds to get cookies (one-time per run)

## Recommendation

**Enable auto-refresh** - Set `AUTO_REFRESH_COOKIES=true` in GitHub Secrets. This way you never have to manually update cookies again!
