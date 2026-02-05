"""
Check if e-play.pl/umowy/ is server-side rendered or uses API
"""
from curl_cffi import requests
from bs4 import BeautifulSoup
import json

url = 'https://e-play.pl/umowy/'

print("Fetching page...")
response = requests.get(url, impersonate="chrome")

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
print(f"Content Length: {len(response.text)} bytes\n")

# Check if HTML contains the data
soup = BeautifulSoup(response.text, 'html.parser')
contracts = soup.find_all('li', class_='contract')

print(f"Found {len(contracts)} contracts in HTML\n")

if contracts:
    print("✅ SERVER-SIDE RENDERED - Data is in HTML")
    print("\nSample contract:")
    contract = contracts[0]
    print(contract.prettify()[:500])
else:
    print("❌ No contracts found in HTML - might be API-based")
    print("\nChecking for API calls in page source...")
    
    # Look for API endpoints in JavaScript
    if 'api' in response.text.lower() or 'fetch' in response.text.lower():
        print("Found API/fetch references in page")
    else:
        print("No obvious API calls found")
