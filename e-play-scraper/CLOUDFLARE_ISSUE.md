# Cloudflare Blocking Automated Browsers

## Issue

Cloudflare is detecting and blocking automated browsers (Playwright), even with stealth settings. This means:

- ✅ Cookies are retrieved successfully
- ❌ But they're not valid for the API endpoint (403 errors)

## Solutions

### Option 1: Use Manual Cookies (Recommended)

**This is the most reliable solution:**

1. **Disable auto-refresh:**
   - Remove or set `AUTO_REFRESH_COOKIES` = `false` in GitHub Secrets

2. **Get cookies from your browser:**
   - Open Chrome → Go to https://e-play.pl/umowy/
   - Press F12 → Application → Cookies → https://e-play.pl
   - Copy `cf_clearance` value

3. **Add to GitHub Secrets:**
   - `CF_CLEARANCE` = your cookie value
   - Update it when it expires (usually every few days/weeks)

**Pros:** ✅ Reliable, works 100%  
**Cons:** ❌ Need to update manually when cookies expire

---

### Option 2: Use Cloudflare Bypass Service

Services like:
- 2captcha (solves Cloudflare challenges)
- Anti-Captcha
- CapSolver

**Pros:** ✅ Fully automated  
**Cons:** ❌ Costs money, adds complexity

---

### Option 3: Accept Limitations

Keep auto-refresh enabled but understand:
- It may work sometimes
- It may fail when Cloudflare tightens security
- You'll need manual cookies as backup

---

## Recommendation

**Use Option 1 (Manual Cookies)** - It's the most reliable and free solution. You only need to update cookies every few weeks, which takes 2 minutes.

## Quick Fix

1. Go to GitHub → Settings → Secrets → Actions
2. Remove `AUTO_REFRESH_COOKIES` secret (or set to `false`)
3. Add `CF_CLEARANCE` secret with cookie from your browser
4. Re-run workflow

That's it! It will work reliably.
