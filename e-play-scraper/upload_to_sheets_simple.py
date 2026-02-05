"""
Simple Google Sheets upload using gspread
Modern version with google-auth
"""
import json
import gspread
from google.oauth2.service_account import Credentials
import os

# Configuration
SCOPE = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

CREDENTIALS_FILE = 'credentials.json'  # Service account JSON file
SPREADSHEET_NAME = 'E-Play Contracts'  # Your Google Sheet name
WORKSHEET_NAME = 'Contracts'  # Tab name


def upload_contracts():
    """Upload contracts to Google Sheets"""
    # Load contracts
    print("Loading contracts...")
    with open('contracts.json', 'r', encoding='utf-8') as f:
        contracts = json.load(f)
    
    print(f"Found {len(contracts)} contracts")
    
    # Authenticate
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"\nERROR: {CREDENTIALS_FILE} not found!")
        print_setup_instructions()
        return
    
    print("Authenticating...")
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPE)
    client = gspread.authorize(creds)
    
    # Open or create spreadsheet
    try:
        spreadsheet = client.open(SPREADSHEET_NAME)
        print(f"Opened: {SPREADSHEET_NAME}")
    except gspread.exceptions.SpreadsheetNotFound:
        spreadsheet = client.create(SPREADSHEET_NAME)
        print(f"Created: {SPREADSHEET_NAME}")
    
    # Get worksheet
    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=10000, cols=15)
    
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
    print(f"Uploading {len(contracts)} rows...")
    worksheet.clear()
    worksheet.update('A1', rows, value_input_option='RAW')
    
    # Format header
    worksheet.format('A1:M1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
    })
    
    print(f"\nDone! Sheet: {spreadsheet.url}")


def print_setup_instructions():
    print("\n" + "="*60)
    print("  GOOGLE SHEETS SETUP INSTRUCTIONS")
    print("="*60)
    print("\n1. Go to: https://console.cloud.google.com/")
    print("2. Create a project (or select existing)")
    print("3. Enable APIs:")
    print("   - Google Sheets API")
    print("   - Google Drive API")
    print("4. Go to: APIs & Services → Credentials")
    print("5. Create Credentials → Service Account")
    print("6. Create Service Account → Download JSON key")
    print("7. Save JSON file as 'credentials.json' in this folder")
    print("8. Copy the service account email (ends with @...gserviceaccount.com)")
    print("9. Create a Google Sheet and share it with that email")
    print("10. Update SPREADSHEET_NAME in this script to match your sheet name")
    print("\n" + "="*60)


if __name__ == '__main__':
    upload_contracts()
