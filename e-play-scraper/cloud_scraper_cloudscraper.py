"""
Scraper using cloudscraper directly (no cookie extraction needed)
This bypasses Cloudflare automatically
"""
import json
import os
import time
import random

API_URL = 'https://e-play.pl/wp-json/contracts/v1/filter'
DELAY_BETWEEN_PAGES = (0.5, 1)

# Google Sheets config
UPLOAD_TO_SHEETS = os.getenv('UPLOAD_TO_SHEETS', 'false').lower() == 'true'
SHEETS_CREDENTIALS_JSON = os.getenv('SHEETS_CREDENTIALS_JSON', '')
SHEETS_SPREADSHEET_NAME = os.getenv('SHEETS_SPREADSHEET_NAME', 'E-Play Contracts')
SHEETS_WORKSHEET_NAME = os.getenv('SHEETS_WORKSHEET_NAME', 'Contracts')


def get_scraper():
    """Get cloudscraper instance"""
    try:
        import cloudscraper
    except ImportError:
        print("Installing cloudscraper...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cloudscraper"])
        import cloudscraper
    
    # Create scraper (handles Cloudflare automatically)
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    return scraper


def fetch_contracts_page(scraper, page=1, quantity=120):
    """Fetch one page using cloudscraper"""
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
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Origin': 'https://e-play.pl',
        'Referer': 'https://e-play.pl/umowy/'
    }
    
    try:
        response = scraper.post(API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            print(f"⚠️  Got 403 on page {page} - Cloudflare blocking")
            print(f"   Response: {response.text[:200]}")
            return None
        else:
            print(f"⚠️  Got status {response.status_code} on page {page}")
            response.raise_for_status()
            return None
            
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
        return None


def scrape_all_contracts():
    """Scrape all contracts with pagination"""
    print("Initializing cloudscraper (solving Cloudflare challenge)...")
    scraper = get_scraper()
    
    # Visit the page first to get cookies
    print("Visiting e-play.pl to establish session...")
    try:
        response = scraper.get('https://e-play.pl/umowy/', timeout=30)
        if response.status_code == 200:
            print("✓ Session established")
        else:
            print(f"⚠️  Got status {response.status_code} on initial visit")
    except Exception as e:
        print(f"⚠️  Initial visit failed: {e}")
        print("   Continuing anyway...")
    
    all_contracts = []
    page = 1
    quantity = 120
    total_pages = None
    
    while True:
        data = fetch_contracts_page(scraper, page, quantity)
        
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
        worksheet.update(values=rows, range_name='A1', value_input_option='RAW')
        
        worksheet.format('A1:M1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        
        print(f"✓ Uploaded to Google Sheets: {spreadsheet.url}")
        return True
        
    except Exception as e:
        print(f"✗ Google Sheets upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("Starting E-Play scraper with cloudscraper (auto Cloudflare bypass)...")
    
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
