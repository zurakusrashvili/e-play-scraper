# How to Get Cookies for GitHub Actions

## Option 1: Extract from cURL Command (Easiest)

If you have a cURL command with cookies:

1. **Run the extractor:**
   ```bash
   python extract_cookies_from_curl.py
   ```

2. **Paste your cURL command** (or provide as argument):
   ```bash
   python extract_cookies_from_curl.py "curl -H 'Cookie: cf_clearance=...' ..."
   ```

3. **Copy the output** - it will show:
   - Python format (for local scripts)
   - Environment variables (for GitHub Secrets)

---

## Option 2: From Browser (Current Method)

1. Open Chrome → Go to: https://e-play.pl/umowy/
2. Press `F12` → `Application` tab → `Cookies` → `https://e-play.pl`
3. Copy these cookie values:
   - `cf_clearance` → Use for `CF_CLEARANCE` secret
   - `_ga` → Use for `GA_COOKIE` secret (optional)
   - `_ga_ZH4G2KK1JY` → Use for `GA_ZH4G2KK1JY` secret (optional)

---

## Option 3: Use Existing Cookies from Code

We already have cookies in `scrape_contracts_api.py`:

```python
COOKIES = {
    'cf_clearance': '7CT8gc2BBltU03qgc.HPPzBhqpH62fXbdFW.p8qfutU-1770296575-1.2.1.1-OGmfWH.SiF5USXu_Ma3jdC1a83qhIbhtv4A0i.OMMNMBbGIL_Suy5ScB7rL8QEe_zrVkFkCsohanunokILXi69YY6hZGRrnvo5JAhuslQ57H4dspPHz05eJQ8VLzSdzsmeA_mSlqgAeyfxhheLcAwHbcntSIDvE3uDdYyStavQzzBWpjp.Xnv4UJROit.5VaWhENthy9A9gh.md0tVHoMu7yGYgfwWl3YsUGm92obog',
    '_ga': 'GA1.1.783563484.1770296575',
    '_ga_ZH4G2KK1JY': 'GS2.1.s1770296575$o1$g1$t1770296600$j35$l0$h0'
}
```

**For GitHub Secrets, use:**
- `CF_CLEARANCE` = `7CT8gc2BBltU03qgc.HPPzBhqpH62fXbdFW.p8qfutU-1770296575-1.2.1.1-OGmfWH.SiF5USXu_Ma3jdC1a83qhIbhtv4A0i.OMMNMBbGIL_Suy5ScB7rL8QEe_zrVkFkCsohanunokILXi69YY6hZGRrnvo5JAhuslQ57H4dspPHz05eJQ8VLzSdzsmeA_mSlqgAeyfxhheLcAwHbcntSIDvE3uDdYyStavQzzBWpjp.Xnv4UJROit.5VaWhENthy9A9gh.md0tVHoMu7yGYgfwWl3YsUGm92obog`
- `GA_COOKIE` = `GA1.1.783563484.1770296575`
- `GA_ZH4G2KK1JY` = `GS2.1.s1770296575$o1$g1$t1770296600$j35$l0$h0`

**⚠️ Note:** These cookies may expire! If the scraper stops working, get fresh ones.

---

## Quick Copy for GitHub Secrets

If you want to use the existing cookies from the code:

1. Go to: GitHub Repo → Settings → Secrets → Actions
2. Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `CF_CLEARANCE` | `7CT8gc2BBltU03qgc.HPPzBhqpH62fXbdFW.p8qfutU-1770296575-1.2.1.1-OGmfWH.SiF5USXu_Ma3jdC1a83qhIbhtv4A0i.OMMNMBbGIL_Suy5ScB7rL8QEe_zrVkFkCsohanunokILXi69YY6hZGRrnvo5JAhuslQ57H4dspPHz05eJQ8VLzSdzsmeA_mSlqgAeyfxhheLcAwHbcntSIDvE3uDdYyStavQzzBWpjp.Xnv4UJROit.5VaWhENthy9A9gh.md0tVHoMu7yGYgfwWl3YsUGm92obog` |
| `GA_COOKIE` | `GA1.1.783563484.1770296575` |
| `GA_ZH4G2KK1JY` | `GS2.1.s1770296575$o1$g1$t1770296600$j35$l0$h0` |

---

## Testing Cookies

To test if cookies are still valid:

```bash
cd e-play-scraper
python test_api.py
```

If it works, cookies are good! If you get 403/401 errors, get fresh cookies.
