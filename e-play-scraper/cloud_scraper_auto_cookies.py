"""
Cloud-ready scraper with automatic cookie refresh
Gets fresh cookies before scraping if needed
"""
from curl_cffi import requests
import json
import os
import time
import random
import subprocess
import sys

API_URL = 'https://e-play.pl/wp-json/contracts/v1/filter'
DELAY_BETWEEN_PAGES = (0.5, 1)

# Google Sheets config
UPLOAD_TO_SHEETS = os.getenv('UPLOAD_TO_SHEETS', 'false').lower() == 'true'
SHEETS_CREDENTIALS_JSON = os.getenv('SHEETS_CREDENTIALS_JSON', '')
SHEETS_SPREADSHEET_NAME = os.getenv('SHEETS_SPREADSHEET_NAME', 'E-Play Contracts')
SHEETS_WORKSHEET_NAME = os.getenv('SHEETS_WORKSHEET_NAME', 'Contracts')

# Cookie refresh config
AUTO_REFRESH_COOKIES = os.getenv('AUTO_REFRESH_COOKIES', 'true').lower() == 'true'
COOKIE_REFRESH_SCRIPT = 'get_cookies_automated.py'


def get_cookies_from_env():
    """Get cookies from environment variables"""
    return {
        'cf_clearance': os.getenv('CF_CLEARANCE', ''),
        '_ga': os.getenv('GA_COOKIE', ''),
        '_ga_ZH4G2KK1JY': os.getenv('GA_ZH4G2KK1JY', '')
    }


def refresh_cookies_automated():
    """Refresh cookies using automated browser"""
    print("Attempting to refresh cookies automatically...")
    
    # Try the new method first (via API)
    try:
        from get_cookies_via_browser_api import get_cookies_via_api
        cookies = get_cookies_via_api()
        if cookies and cookies.get('cf_clearance'):
            print("✓ Got cookies via browser API method")
            return cookies
    except Exception as e:
        print(f"Browser API method failed: {e}, trying fallback...")
    
    # Fallback to original method
    try:
        # Try to run the cookie refresh script
        result = subprocess.run(
            [sys.executable, COOKIE_REFRESH_SCRIPT],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Try to read from .env.cookies file
            env_file = '.env.cookies'
            if os.path.exists(env_file):
                cookies = {}
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            cookies[key.strip()] = value.strip()
                
                if cookies.get('CF_CLEARANCE'):
                    print("✓ Successfully refreshed cookies")
                    return {
                        'cf_clearance': cookies.get('CF_CLEARANCE', ''),
                        '_ga': cookies.get('GA_COOKIE', ''),
                        '_ga_ZH4G2KK1JY': cookies.get('GA_ZH4G2KK1JY', '')
                    }
        
        print("⚠️  Cookie refresh script didn't return valid cookies")
        return None
        
    except subprocess.TimeoutExpired:
        print("✗ Cookie refresh timed out")
        return None
    except Exception as e:
        print(f"✗ Error refreshing cookies: {e}")
        return None


def get_cookies():
    """Get cookies - try auto-refresh first, fallback to env vars"""
    cookies = get_cookies_from_env()
    
    # Check if we have valid cookies
    if not cookies.get('cf_clearance'):
        print("⚠️  No CF_CLEARANCE in environment variables")
        
        if AUTO_REFRESH_COOKIES:
            print("Attempting automatic cookie refresh...")
            refreshed = refresh_cookies_automated()
            if refreshed and refreshed.get('cf_clearance'):
                return refreshed
        
        print("ERROR: No cookies available!")
        return None
    
    # Test cookies by making a request
    print("Testing cookies...")
    test_result = test_cookies(cookies)
    
    if not test_result and AUTO_REFRESH_COOKIES:
        print("Cookies appear invalid, attempting refresh...")
        refreshed = refresh_cookies_automated()
        if refreshed and refreshed.get('cf_clearance'):
            return refreshed
    
    return cookies


def test_cookies(cookies):
    """Test if cookies work by making a test request"""
    try:
        headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'origin': 'https://e-play.pl',
            'referer': 'https://e-play.pl/umowy/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        payload = {'paged': 1, 'quantity': 1}
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            cookies=cookies,
            timeout=10,
            impersonate="chrome"
        )
        
        if response.status_code == 200:
            print("✓ Cookies are valid")
            return True
        else:
            print(f"⚠️  Cookies test returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  Cookie test failed: {e}")
        return False


# Headers
HEADERS = {
    'accept': '*/*',
    'accept-language': 'ka-GE,ka;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://e-play.pl',
    'pragma': 'no-cache',
    'referer': 'https://e-play.pl/umowy/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
}


def fetch_contracts_page(page=1, quantity=120, cookies=None):
    """Fetch one page of contracts from API"""
    if not cookies:
        cookies = get_cookies()
        if not cookies:
            return None
    
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
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_URL,
                json=payload,
                headers=HEADERS,
                cookies=cookies,
                timeout=30,
                impersonate="chrome"
            )
            
            # Check status code
            if response.status_code == 403:
                print(f"Got 403 on page {page} (attempt {attempt + 1}/{max_retries})")
                if AUTO_REFRESH_COOKIES and attempt < max_retries - 1:
                    print("Refreshing cookies and retrying...")
                    refreshed = refresh_cookies_automated()
                    if refreshed and refreshed.get('cf_clearance'):
                        cookies = refreshed
                        time.sleep(2)  # Wait a bit before retry
                        continue
                else:
                    print("403 error persists - cookies may not be valid for API")
                    print(f"Response: {response.text[:200]}")
                    return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 403:
                print(f"HTTP 403 error on page {page}: {e}")
                if AUTO_REFRESH_COOKIES and attempt < max_retries - 1:
                    print("Refreshing cookies and retrying...")
                    refreshed = refresh_cookies_automated()
                    if refreshed and refreshed.get('cf_clearance'):
                        cookies = refreshed
                        time.sleep(2)
                        continue
                return None
            raise
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            if attempt < max_retries - 1 and AUTO_REFRESH_COOKIES:
                print("Retrying with fresh cookies...")
                refreshed = refresh_cookies_automated()
                if refreshed:
                    cookies = refreshed
                    time.sleep(2)
                    continue
            return None
    
    return None


def scrape_all_contracts():
    """Scrape all contracts with pagination"""
    # Get cookies once at start
    cookies = get_cookies()
    if not cookies:
        print("ERROR: Could not get cookies!")
        return []
    
    all_contracts = []
    page = 1
    quantity = 120
    total_pages = None
    
    while True:
        data = fetch_contracts_page(page, quantity, cookies)
        
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
            contract = {
                'id': item.get('id', ''),
                'link': item.get('url', ''),
                'company1': item.get('company1', {}).get('name', ''),
                'company2': item.get('company2', {}).get('name', ''),
                'subjects': item.get('subject', ''),
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
        try:
            creds_json = json.loads(base64.b64decode(SHEETS_CREDENTIALS_JSON).decode('utf-8'))
        except:
            creds_json = json.loads(SHEETS_CREDENTIALS_JSON)
        
        SCOPE = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_info(creds_json, scopes=SCOPE)
        client = gspread.authorize(creds)
        
        try:
            spreadsheet = client.open(SHEETS_SPREADSHEET_NAME)
        except gspread.exceptions.SpreadsheetNotFound:
            spreadsheet = client.create(SHEETS_SPREADSHEET_NAME)
        
        try:
            worksheet = spreadsheet.worksheet(SHEETS_WORKSHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=SHEETS_WORKSHEET_NAME, rows=10000, cols=15)
        
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
        
        worksheet.clear()
        worksheet.update('A1', rows, value_input_option='RAW')
        
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
    print("Starting E-Play scraper with auto-cookie refresh...")
    
    contracts = scrape_all_contracts()
    print(f"\nTotal contracts found: {len(contracts)}")
    
    if UPLOAD_TO_SHEETS:
        upload_to_google_sheets(contracts)
    else:
        print("Google Sheets upload disabled (set UPLOAD_TO_SHEETS=true to enable)")
    
    print("Done!")
    return contracts


if __name__ == '__main__':
    main()
