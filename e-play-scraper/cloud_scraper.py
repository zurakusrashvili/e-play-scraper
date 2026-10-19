"""
Cloud-ready version of the scraper
Uses environment variables for configuration
Hits the e-play.com API directly with curl_cffi (no cookies, no Cloudflare bypass)
"""
from curl_cffi import requests
import json
import os
import sys
import subprocess
import time
import random

HEADERS = {
    'accept': '*/*',
    'accept-language': 'ka-GE,ka;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://e-play.com',
    'pragma': 'no-cache',
    'referer': 'https://e-play.com/deals/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
}

API_URL = 'https://e-play.com/wp-json/contracts/v1/filter'
DELAY_BETWEEN_PAGES = (0.5, 1)

# Google Sheets config
UPLOAD_TO_SHEETS = os.getenv('UPLOAD_TO_SHEETS', 'false').lower() == 'true'
SHEETS_CREDENTIALS_JSON = os.getenv('SHEETS_CREDENTIALS_JSON', '')  # Base64 or JSON string
SHEETS_SPREADSHEET_NAME = os.getenv('SHEETS_SPREADSHEET_NAME', 'E-Play Contracts')
SHEETS_WORKSHEET_NAME = os.getenv('SHEETS_WORKSHEET_NAME', 'Contracts')

# Cloudflare fallback state
_cloudscraper_session = None   # lazily created cloudscraper instance
_fallback_active = False       # once True, use cloudscraper for all remaining pages
_fallback_engaged = False      # True if fallback was EVER used this run (for final reporting)


def _get_cloudscraper():
    """Lazily create + cache a cloudscraper session (install on demand)."""
    global _cloudscraper_session

    if _cloudscraper_session is not None:
        return _cloudscraper_session

    try:
        import cloudscraper
    except ImportError:
        print("Installing cloudscraper...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cloudscraper"])
        import cloudscraper

    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    # Best-effort: establish a session by visiting the deals page first.
    try:
        scraper.get('https://e-play.com/deals/', timeout=30)
    except Exception as e:
        print(f"[WARN] cloudscraper session warm-up failed (continuing): {e}")

    _cloudscraper_session = scraper
    return _cloudscraper_session


def fetch_contracts_page(page=1, quantity=120):
    """Fetch one page of contracts from API (direct curl_cffi, with cloudscraper 403 fallback)."""
    global _fallback_active, _fallback_engaged

    payload = {
        'paged': page,
        'quantity': quantity,
        'subject': '',
        'retail': '',
        'acquisition': '',
        'startup': '',
        'rebranding': '',
        'payments': '',
        'date_from': '',
        'date_to': ''
    }

    # Direct curl_cffi attempt (happy path, no cookies) unless fallback already engaged.
    if not _fallback_active:
        try:
            response = requests.post(
                API_URL,
                json=payload,
                headers=HEADERS,
                timeout=30,
                impersonate="chrome"
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                print(f"[WARN] Direct request got 403 on page {page} — switching to cloudscraper fallback")
                _fallback_active = True
                _fallback_engaged = True
                # fall through to cloudscraper branch
            else:
                print(f"[WARN] Unexpected status {response.status_code} on page {page}")
                return None
        except Exception as e:
            print(f"[WARN] Direct request failed on page {page} ({e}) — switching to cloudscraper fallback")
            _fallback_active = True
            _fallback_engaged = True
            # fall through to cloudscraper branch

    # Cloudscraper fallback branch.
    try:
        scraper = _get_cloudscraper()
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Origin': 'https://e-play.com',
            'Referer': 'https://e-play.com/deals/'
        }
        response = scraper.post(API_URL, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        print(f"[WARN] cloudscraper also got status {response.status_code} on page {page}")
        return None
    except Exception as e:
        print(f"[WARN] cloudscraper request failed on page {page}: {e}")
        return None


def scrape_all_contracts():
    """Scrape all contracts with pagination"""
    all_contracts = []
    page = 1
    quantity = 120
    total_pages = None

    while True:
        data = fetch_contracts_page(page, quantity)

        if not data:
            break

        items = data.get('items', [])
        pagination = data.get('pagination', {})

        if total_pages is None:
            total_pages = pagination.get('total_pages', 1)
            print(f"Total pages: {total_pages}")

        if not items:
            break

        for item in items:
            # Try multiple ways to get company names (API structure might vary)
            company1 = ''
            company2 = ''

            # Method 1: subject1/subject2 (most common)
            if item.get('subject1'):
                company1 = item.get('subject1', '')
            if item.get('subject2'):
                company2 = item.get('subject2', '')

            # Method 2: company1/company2 objects
            if not company1 and item.get('company1'):
                company1 = item.get('company1', {}).get('name', '') if isinstance(item.get('company1'), dict) else str(item.get('company1', ''))
            if not company2 and item.get('company2'):
                company2 = item.get('company2', {}).get('name', '') if isinstance(item.get('company2'), dict) else str(item.get('company2', ''))

            # Get subjects
            subjects = item.get('subject', '')
            if not subjects and company1 and company2:
                subjects = f"{company1} 🤝 {company2}"
            elif not subjects and company1:
                subjects = company1

            contract = {
                'id': item.get('id', ''),
                'link': item.get('url', ''),
                'company1': company1,
                'company2': company2,
                'subjects': subjects,
                'date': item.get('date', ''),
                'country': item.get('market', [''])[0].upper() if item.get('market') else '',
                'markets': ', '.join(item.get('market', [])),
                'contract_slug': item.get('url', '').split('/')[-2] if item.get('url') else '',
                'flags': {
                    'retail': item.get('flags', {}).get('retail', False),
                    'acquisition': item.get('flags', {}).get('acquisition', False),
                    'startup': item.get('flags', {}).get('startup', False),
                    'rebranding': item.get('flags', {}).get('rebranding', False)
                }
            }
            all_contracts.append(contract)

        current_page = pagination.get('page', page)
        response_total_pages = pagination.get('total_pages', total_pages or 1)

        if total_pages != response_total_pages:
            total_pages = response_total_pages

        print(f"Page {current_page}/{total_pages}: {len(items)} contracts (total: {len(all_contracts)})")

        if current_page >= total_pages:
            break

        if len(items) == 0:
            break

        page += 1
        delay = random.uniform(*DELAY_BETWEEN_PAGES)
        time.sleep(delay)

    return all_contracts


def upload_to_google_sheets(contracts):
    """Upload contracts to Google Sheets"""
    if not contracts:
        print("[ABORT] Refusing to upload 0 contracts — would wipe the sheet. Skipping upload.")
        return False

    try:
        import gspread
        from google.oauth2.service_account import Credentials
        import base64
    except ImportError:
        print("gspread not installed, skipping Google Sheets upload")
        return False

    if not SHEETS_CREDENTIALS_JSON:
        print("SHEETS_CREDENTIALS_JSON not set, skipping upload")
        return False

    try:
        # Parse credentials (can be base64 or JSON string)
        try:
            # Try base64 decode first
            creds_json = json.loads(base64.b64decode(SHEETS_CREDENTIALS_JSON).decode('utf-8'))
        except:
            # If not base64, try direct JSON
            creds_json = json.loads(SHEETS_CREDENTIALS_JSON)

        SCOPE = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = Credentials.from_service_account_info(creds_json, scopes=SCOPE)
        client = gspread.authorize(creds)

        # Open spreadsheet
        try:
            spreadsheet = client.open(SHEETS_SPREADSHEET_NAME)
        except gspread.exceptions.SpreadsheetNotFound:
            spreadsheet = client.create(SHEETS_SPREADSHEET_NAME)

        # Get worksheet
        try:
            worksheet = spreadsheet.worksheet(SHEETS_WORKSHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=SHEETS_WORKSHEET_NAME, rows=10000, cols=15)

        # Prepare data
        headers = [
            'ID', 'Link', 'Company 1', 'Company 2', 'Subjects',
            'Date', 'Country', 'Markets', 'Contract Slug',
            'Retail', 'Acquisition', 'Startup', 'Rebranding'
        ]

        rows = [headers]
        for c in contracts:
            rows.append([
                c.get('id', ''),
                c.get('link', ''),
                c.get('company1', ''),
                c.get('company2', ''),
                c.get('subjects', ''),
                c.get('date', ''),
                c.get('country', ''),
                c.get('markets', ''),
                c.get('contract_slug', ''),
                'Yes' if c.get('flags', {}).get('retail') else '',
                'Yes' if c.get('flags', {}).get('acquisition') else '',
                'Yes' if c.get('flags', {}).get('startup') else '',
                'Yes' if c.get('flags', {}).get('rebranding') else ''
            ])

        # Upload
        worksheet.clear()
        worksheet.update(values=rows, range_name='A1', value_input_option='RAW')

        # Format header
        worksheet.format('A1:M1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })

        print(f"✓ Uploaded to Google Sheets: {spreadsheet.url}")
        return True

    except Exception as e:
        print(f"✗ Google Sheets upload failed: {e}")
        return False


def main():
    """Main function for cloud execution"""
    print("Starting E-Play scraper...")

    contracts = scrape_all_contracts()
    print(f"\nTotal contracts found: {len(contracts)}")

    # Data-safety: a run that scraped nothing is almost certainly a block or an
    # API change. Never upload (an empty upload would wipe the sheet) and fail loudly.
    if len(contracts) == 0:
        print("\n" + "=" * 70)
        print("[FATAL] Scraped 0 contracts — likely blocked by Cloudflare or the API changed.")
        print("[FATAL] Not uploading (sheet left intact).")
        print("=" * 70)
        sys.exit(1)

    # Upload to Google Sheets (if enabled). Empty case already exited above.
    if UPLOAD_TO_SHEETS and contracts:
        upload_to_google_sheets(contracts)
    else:
        print("Google Sheets upload disabled (set UPLOAD_TO_SHEETS=true to enable)")

    if _fallback_engaged:
        print("\n" + "=" * 70)
        print("[NOTE] Direct access was blocked this run; data was retrieved via cloudscraper fallback.")
        print("[NOTE] Consider checking Cloudflare status.")
        print("=" * 70)

    print("Done!")
    return contracts


if __name__ == '__main__':
    main()
