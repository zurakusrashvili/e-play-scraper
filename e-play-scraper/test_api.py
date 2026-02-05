"""
Quick test to see API response format
"""
from curl_cffi import requests
import json

COOKIES = {
    'cf_clearance': '7CT8gc2BBltU03qgc.HPPzBhqpH62fXbdFW.p8qfutU-1770296575-1.2.1.1-OGmfWH.SiF5USXu_Ma3jdC1a83qhIbhtv4A0i.OMMNMBbGIL_Suy5ScB7rL8QEe_zrVkFkCsohanunokILXi69YY6hZGRrnvo5JAhuslQ57H4dspPHz05eJQ8VLzSdzsmeA_mSlqgAeyfxhheLcAwHbcntSIDvE3uDdYyStavQzzBWpjp.Xnv4UJROit.5VaWhENthy9A9gh.md0tVHoMu7yGYgfwWl3YsUGm92obog',
    '_ga': 'GA1.1.783563484.1770296575',
    '_ga_ZH4G2KK1JY': 'GS2.1.s1770296575$o1$g1$t1770296600$j35$l0$h0'
}

HEADERS = {
    'accept': '*/*',
    'content-type': 'application/json',
    'origin': 'https://e-play.pl',
    'referer': 'https://e-play.pl/umowy/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

payload = {
    "paged": 1,
    "quantity": 120,
    "subject": "",
    "retail": "",
    "acquisition": "",
    "startup": "",
    "rebranding": "",
    "payments": "",
    "date_from": "",
    "date_to": ""
}

print("Testing API...")
response = requests.post(
    'https://e-play.pl/wp-json/contracts/v1/filter',
    headers=HEADERS,
    cookies=COOKIES,
    json=payload,
    impersonate="chrome"
)

print(f"Status: {response.status_code}")
print(f"\nResponse keys: {list(response.json().keys()) if response.status_code == 200 else 'ERROR'}")
print(f"\nResponse preview:")
print(json.dumps(response.json(), indent=2)[:2000])
