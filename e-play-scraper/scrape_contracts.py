"""
Scrape contracts from e-play.pl/umowy/
Extracts: subjects, date, flag, and link
"""
from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import csv
import re

url = 'https://e-play.pl/umowy/'

print("Fetching contracts page...")
response = requests.get(url, impersonate="chrome")

if response.status_code != 200:
    print(f"Error: Status {response.status_code}")
    exit(1)

soup = BeautifulSoup(response.text, 'html.parser')
contracts = soup.find_all('li', class_='contract')

print(f"Found {len(contracts)} contracts\n")

results = []

for contract in contracts:
    link_elem = contract.find('a')
    if not link_elem:
        continue
    
    # Extract link
    link = link_elem.get('href', '')
    
    # Extract subjects (e.g., "Stakelogic 🤝 Casino Gran Madrid")
    subjects_elem = link_elem.find('div', class_='subjects')
    subjects = subjects_elem.get_text(strip=True) if subjects_elem else ''
    
    # Extract date (e.g., "05/02/2026")
    date_elem = link_elem.find('div', class_='date')
    date = date_elem.get_text(strip=True) if date_elem else ''
    
    # Extract flag (country code from class like "flag-es")
    flags_elem = link_elem.find('div', class_='flags')
    flag = ''
    if flags_elem:
        flag_elem = flags_elem.find('div', class_=re.compile('^flag flag-'))
        if flag_elem:
            flag_class = flag_elem.get('class', [])
            for cls in flag_class:
                if cls.startswith('flag-'):
                    flag = cls.replace('flag-', '').upper()  # "es" -> "ES"
                    break
    
    # Parse subjects to get individual companies
    # Format: "Company1 🤝 Company2"
    companies = []
    if '🤝' in subjects:
        parts = subjects.split('🤝')
        companies = [p.strip() for p in parts]
    else:
        companies = [subjects]
    
    result = {
        'link': link,
        'subjects': subjects,
        'company1': companies[0] if len(companies) > 0 else '',
        'company2': companies[1] if len(companies) > 1 else '',
        'date': date,
        'country': flag,
        'contract_slug': link.split('/')[-2] if link else ''  # Extract slug from URL
    }
    
    results.append(result)
    print(f"  - {subjects} | {date} | {flag}")

# Save as JSON
with open('contracts.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(results)} contracts to contracts.json")

# Save as CSV
with open('contracts.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['link', 'subjects', 'company1', 'company2', 'date', 'country', 'contract_slug'])
    writer.writeheader()
    writer.writerows(results)

print(f"Saved {len(results)} contracts to contracts.csv")
