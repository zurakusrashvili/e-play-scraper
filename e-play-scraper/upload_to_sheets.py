"""
Upload contracts to Google Sheets
Requires: pip install gspread oauth2client
"""
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Configuration
SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# You need to:
# 1. Create a Google Cloud Project
# 2. Enable Google Sheets API
# 3. Create Service Account credentials
# 4. Download JSON key file
# 5. Share your Google Sheet with the service account email
CREDENTIALS_FILE = 'credentials.json'  # Your service account JSON file
SPREADSHEET_NAME = 'E-Play Contracts'  # Name of your Google Sheet
WORKSHEET_NAME = 'Contracts'  # Tab name (or leave empty for first sheet)


def authenticate():
    """Authenticate with Google Sheets API"""
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"ERROR: {CREDENTIALS_FILE} not found!")
        print("\nTo set up:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project (or use existing)")
        print("3. Enable 'Google Sheets API' and 'Google Drive API'")
        print("4. Create Service Account → Download JSON key")
        print("5. Save it as 'credentials.json' in this folder")
        print("6. Share your Google Sheet with the service account email")
        return None
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    client = gspread.authorize(creds)
    return client


def upload_contracts():
    """Upload contracts from JSON to Google Sheets"""
    # Load contracts
    print("Loading contracts from contracts.json...")
    with open('contracts.json', 'r', encoding='utf-8') as f:
        contracts = json.load(f)
    
    print(f"Found {len(contracts)} contracts")
    
    # Authenticate
    print("\nAuthenticating with Google Sheets...")
    client = authenticate()
    if not client:
        return
    
    # Open or create spreadsheet
    try:
        spreadsheet = client.open(SPREADSHEET_NAME)
        print(f"Opened existing sheet: {SPREADSHEET_NAME}")
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Creating new sheet: {SPREADSHEET_NAME}")
        spreadsheet = client.create(SPREADSHEET_NAME)
    
    # Get or create worksheet
    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        print(f"Using existing worksheet: {WORKSHEET_NAME}")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=10000, cols=20)
        print(f"Created new worksheet: {WORKSHEET_NAME}")
    
    # Prepare data
    headers = [
        'ID', 'Link', 'Company 1', 'Company 2', 'Subjects', 
        'Date', 'Country', 'Markets', 'Contract Slug',
        'Flag: Retail', 'Flag: Acquisition', 'Flag: Startup', 'Flag: Rebranding'
    ]
    
    rows = [headers]
    for c in contracts:
        row = [
            c.get('id', ''),
            c.get('link', ''),
            c.get('company1', ''),
            c.get('company2', ''),
            c.get('subjects', ''),
            c.get('date', ''),
            c.get('country', ''),
            c.get('markets', ''),
            c.get('contract_slug', ''),
            'Yes' if c.get('flags', {}).get('retail') else 'No',
            'Yes' if c.get('flags', {}).get('acquisition') else 'No',
            'Yes' if c.get('flags', {}).get('startup') else 'No',
            'Yes' if c.get('flags', {}).get('rebranding') else 'No'
        ]
        rows.append(row)
    
    # Clear existing data and write new
    print(f"\nUploading {len(contracts)} contracts to Google Sheets...")
    worksheet.clear()
    worksheet.update('A1', rows)
    
    # Format header row
    worksheet.format('A1:N1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
    })
    
    # Auto-resize columns
    worksheet.columns_auto_resize(0, len(headers))
    
    print(f"\nDone! Sheet URL: {spreadsheet.url}")
    print(f"Total rows: {len(rows)}")


if __name__ == '__main__':
    upload_contracts()
