"""
Cloud-ready version of the scraper
Uses environment variables for configuration
"""
from curl_cffi import requests
import json
import os
import time
import random

# Configuration from environment variables
COOKIES = {
    'cf_clearance': os.getenv('CF_CLEARANCE', ''),
    '_ga': os.getenv('GA_COOKIE', ''),
    '_ga_ZH4G2KK1JY': os.getenv('GA_ZH4G2KK1JY', '')
}

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

API_URL = 'https://e-play.pl/wp-json/contracts/v1/filter'
DELAY_BETWEEN_PAGES = (0.5, 1)

# Google Sheets config
UPLOAD_TO_SHEETS = os.getenv('UPLOAD_TO_SHEETS', 'false').lower() == 'true'
SHEETS_CREDENTIALS_JSON = os.getenv('SHEETS_CREDENTIALS_JSON', '')  # Base64 or JSON string
SHEETS_SPREADSHEET_NAME = os.getenv('SHEETS_SPREADSHEET_NAME', 'E-Play Contracts')
SHEETS_WORKSHEET_NAME = os.getenv('SHEETS_WORKSHEET_NAME', 'Contracts')


def fetch_contracts_page(page=1, quantity=120):
    """Fetch one page of contracts from API"""
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
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=HEADERS,
            cookies=COOKIES,
            timeout=30,
            impersonate="chrome"
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
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
        worksheet.update('A1', rows, value_input_option='RAW')
        
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
    
    # Validate cookies
    if not COOKIES.get('cf_clearance'):
        print("ERROR: CF_CLEARANCE environment variable not set!")
        return
    
    contracts = scrape_all_contracts()
    print(f"\nTotal contracts found: {len(contracts)}")
    
    # Upload to Google Sheets (if enabled)
    if UPLOAD_TO_SHEETS:
        upload_to_google_sheets(contracts)
    else:
        print("Google Sheets upload disabled (set UPLOAD_TO_SHEETS=true to enable)")
    
    print("Done!")
    return contracts


if __name__ == '__main__':
    main()
