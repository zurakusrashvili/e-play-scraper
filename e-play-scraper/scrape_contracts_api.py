"""
Scrape contracts from e-play.pl using their API
API: https://e-play.pl/wp-json/contracts/v1/filter
"""
from curl_cffi import requests
import json
import csv
import time
import random
import os

# Optional: Google Sheets upload
# Set UPLOAD_TO_SHEETS = True and configure below
UPLOAD_TO_SHEETS = False  # Set to True to enable Google Sheets upload
SHEETS_CREDENTIALS_FILE = 'credentials.json'  # Service account JSON file
SHEETS_SPREADSHEET_NAME = 'E-Play Contracts'  # Your Google Sheet name
SHEETS_WORKSHEET_NAME = 'Contracts'  # Tab name

# Configuration - UPDATE WITH FRESH COOKIES FROM BROWSER
COOKIES = {
    'cf_clearance': '7CT8gc2BBltU03qgc.HPPzBhqpH62fXbdFW.p8qfutU-1770296575-1.2.1.1-OGmfWH.SiF5USXu_Ma3jdC1a83qhIbhtv4A0i.OMMNMBbGIL_Suy5ScB7rL8QEe_zrVkFkCsohanunokILXi69YY6hZGRrnvo5JAhuslQ57H4dspPHz05eJQ8VLzSdzsmeA_mSlqgAeyfxhheLcAwHbcntSIDvE3uDdYyStavQzzBWpjp.Xnv4UJROit.5VaWhENthy9A9gh.md0tVHoMu7yGYgfwWl3YsUGm92obog',
    '_ga': 'GA1.1.783563484.1770296575',
    '_ga_ZH4G2KK1JY': 'GS2.1.s1770296575$o1$g1$t1770296600$j35$l0$h0'
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

# Delays
DELAY_BETWEEN_PAGES = (0.5, 1)  # Random delay between pages


def fetch_contracts_page(page=1, quantity=120, filters=None):
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
    
    # Add filters if provided
    if filters:
        payload.update(filters)
    
    print(f"Fetching page {page}...")
    
    response = requests.post(
        API_URL,
        headers=HEADERS,
        cookies=COOKIES,
        json=payload,
        impersonate="chrome"
    )
    
    if response.status_code != 200:
        print(f"Error: Status {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return None
    
    return response.json()


def scrape_all_contracts():
    """Scrape all contracts with pagination"""
    all_contracts = []
    page = 1
    quantity = 120  # Max per page
    total_pages = None
    
    while True:
        data = fetch_contracts_page(page, quantity)
        
        if not data:
            break
        
        items = data.get('items', [])
        pagination = data.get('pagination', {})
        
        # Get total pages on first request
        if total_pages is None:
            total_pages = pagination.get('total_pages', 1)
            print(f"\n*** TOTAL PAGES: {total_pages} ***")
            print(f"*** Estimated contracts: ~{total_pages * quantity} ***\n")
        
        if not items:
            print("No more contracts found")
            break
        
        # Process each contract
        for item in items:
            contract = {
                'id': item.get('id'),
                'link': item.get('url'),
                'company1': item.get('subject1', ''),
                'company2': item.get('subject2', ''),
                'subjects': f"{item.get('subject1', '')} 🤝 {item.get('subject2', '')}" if item.get('subject2') else item.get('subject1', ''),  # Emoji in JSON is fine
                'date': item.get('date', ''),
                'country': item.get('market', [''])[0].upper() if item.get('market') else '',  # First market code
                'markets': ', '.join(item.get('market', [])),  # All markets
                'contract_slug': item.get('url', '').split('/')[-2] if item.get('url') else '',
                'flags': {
                    'retail': item.get('flags', {}).get('retail', False),
                    'acquisition': item.get('flags', {}).get('acquisition', False),
                    'startup': item.get('flags', {}).get('startup', False),
                    'rebranding': item.get('flags', {}).get('rebranding', False)
                }
            }
            all_contracts.append(contract)
            try:
                print(f"  - {contract['subjects']} | {contract['date']} | {contract['country']}")
            except UnicodeEncodeError:
                print(f"  - {contract['company1']} x {contract['company2']} | {contract['date']} | {contract['country']}")
        
        # Get current page from response (in case API adjusts it)
        current_page = pagination.get('page', page)
        response_total_pages = pagination.get('total_pages', total_pages or 1)
        
        # Update total_pages if API provides different value
        if total_pages != response_total_pages:
            total_pages = response_total_pages
            print(f"Updated total pages: {total_pages}")
        
        print(f"Page {current_page}/{total_pages}: {len(items)} contracts (total collected: {len(all_contracts)})")
        
        # Stop if we've reached the last page
        if current_page >= total_pages:
            print("Reached last page")
            break
        
        # Also stop if no items returned
        if len(items) == 0:
            print("No items returned - stopping")
            break
        
        page += 1
        delay = random.uniform(*DELAY_BETWEEN_PAGES)
        print(f"Waiting {delay:.1f}s before next page...\n")
        time.sleep(delay)
    
    return all_contracts


def upload_to_google_sheets(contracts):
    """Optional: Upload contracts to Google Sheets"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("\n[SKIP] Google Sheets upload: gspread not installed")
        print("       Install: pip install gspread google-auth")
        return False
    
    if not os.path.exists(SHEETS_CREDENTIALS_FILE):
        print(f"\n[SKIP] Google Sheets upload: {SHEETS_CREDENTIALS_FILE} not found")
        return False
    
    try:
        print("\nUploading to Google Sheets...")
        SCOPE = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(SHEETS_CREDENTIALS_FILE, scopes=SCOPE)
        client = gspread.authorize(creds)
        
        # Open or create spreadsheet
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
    print("=" * 60)
    print("  E-PLAY.PL CONTRACTS SCRAPER (API)")
    print("=" * 60)
    print(f"\nAPI: {API_URL}\n")
    
    contracts = scrape_all_contracts()
    
    print(f"\nTotal contracts found: {len(contracts)}")
    
    # Save as JSON
    with open('contracts.json', 'w', encoding='utf-8') as f:
        json.dump(contracts, f, indent=2, ensure_ascii=False)
    print("Saved to contracts.json")
    
    # Save as CSV (flatten flags)
    if contracts:
        csv_contracts = []
        for c in contracts:
            csv_row = {
                'id': c['id'],
                'link': c['link'],
                'company1': c['company1'],
                'company2': c['company2'],
                'subjects': c['subjects'],
                'date': c['date'],
                'country': c['country'],
                'markets': c['markets'],
                'contract_slug': c['contract_slug'],
                'flag_retail': c['flags']['retail'],
                'flag_acquisition': c['flags']['acquisition'],
                'flag_startup': c['flags']['startup'],
                'flag_rebranding': c['flags']['rebranding']
            }
            csv_contracts.append(csv_row)
        
        with open('contracts.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'link', 'company1', 'company2', 'subjects', 
                'date', 'country', 'markets', 'contract_slug',
                'flag_retail', 'flag_acquisition', 'flag_startup', 'flag_rebranding'
            ])
            writer.writeheader()
            writer.writerows(csv_contracts)
        print("Saved to contracts.csv")
    
    # Optional: Upload to Google Sheets
    if UPLOAD_TO_SHEETS:
        upload_to_google_sheets(contracts)
    
    print("\nDone!")


if __name__ == '__main__':
    main()
