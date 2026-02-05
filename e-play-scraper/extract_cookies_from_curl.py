"""
Extract cookies from a cURL command
Paste your cURL command and it will extract the cookies
"""
import re
import sys

def extract_cookies_from_curl(curl_command):
    """Extract cookies from a cURL command string"""
    cookies = {}
    
    # Pattern 1: -H "Cookie: name=value; name2=value2"
    cookie_header_pattern = r'-H\s+["\']Cookie:\s*([^"\']+)["\']'
    match = re.search(cookie_header_pattern, curl_command, re.IGNORECASE)
    if match:
        cookie_string = match.group(1)
        # Parse cookie string: "name=value; name2=value2"
        for cookie_pair in cookie_string.split(';'):
            cookie_pair = cookie_pair.strip()
            if '=' in cookie_pair:
                name, value = cookie_pair.split('=', 1)
                cookies[name.strip()] = value.strip()
    
    # Pattern 2: --cookie "name=value; name2=value2"
    cookie_flag_pattern = r'--cookie\s+["\']([^"\']+)["\']'
    match = re.search(cookie_flag_pattern, curl_command, re.IGNORECASE)
    if match:
        cookie_string = match.group(1)
        for cookie_pair in cookie_string.split(';'):
            cookie_pair = cookie_pair.strip()
            if '=' in cookie_pair:
                name, value = cookie_pair.split('=', 1)
                cookies[name.strip()] = value.strip()
    
    # Pattern 3: --cookie-jar or -b flag
    cookie_b_pattern = r'[-]b\s+["\']([^"\']+)["\']'
    match = re.search(cookie_b_pattern, curl_command, re.IGNORECASE)
    if match:
        cookie_string = match.group(1)
        for cookie_pair in cookie_string.split(';'):
            cookie_pair = cookie_pair.strip()
            if '=' in cookie_pair:
                name, value = cookie_pair.split('=', 1)
                cookies[name.strip()] = value.strip()
    
    return cookies


def format_for_python(cookies):
    """Format cookies as Python dictionary"""
    if not cookies:
        return None
    
    lines = ["COOKIES = {"]
    for name, value in cookies.items():
        # Escape quotes in value
        escaped_value = value.replace("'", "\\'").replace('"', '\\"')
        lines.append(f"    '{name}': '{escaped_value}',")
    lines.append("}")
    
    return "\n".join(lines)


def format_for_env(cookies):
    """Format cookies as environment variables"""
    if not cookies:
        return None
    
    lines = []
    for name, value in cookies.items():
        # For GitHub Secrets, use uppercase with underscores
        env_name = name.upper().replace('-', '_')
        lines.append(f"{env_name}={value}")
    
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("  EXTRACT COOKIES FROM CURL COMMAND")
    print("=" * 60)
    print("\nPaste your cURL command below (Ctrl+Z then Enter to finish):")
    print("Or provide it as an argument: python extract_cookies_from_curl.py \"curl ...\"")
    print("-" * 60)
    
    # Get cURL command
    if len(sys.argv) > 1:
        curl_command = " ".join(sys.argv[1:])
    else:
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            curl_command = "\n".join(lines)
    
    if not curl_command.strip():
        print("ERROR: No cURL command provided!")
        return
    
    # Extract cookies
    cookies = extract_cookies_from_curl(curl_command)
    
    if not cookies:
        print("\n❌ No cookies found in cURL command!")
        print("\nMake sure your cURL has one of these formats:")
        print('  -H "Cookie: name=value; name2=value2"')
        print('  --cookie "name=value; name2=value2"')
        print('  -b "name=value; name2=value2"')
        return
    
    print(f"\n✓ Found {len(cookies)} cookies:")
    print("-" * 60)
    for name, value in cookies.items():
        # Truncate long values for display
        display_value = value[:50] + "..." if len(value) > 50 else value
        print(f"  {name}: {display_value}")
    
    # Format for Python
    print("\n" + "=" * 60)
    print("  PYTHON FORMAT (for scrape_contracts_api.py)")
    print("=" * 60)
    python_code = format_for_python(cookies)
    print(python_code)
    
    # Format for environment variables
    print("\n" + "=" * 60)
    print("  ENVIRONMENT VARIABLES (for GitHub Secrets)")
    print("=" * 60)
    env_vars = format_for_env(cookies)
    print(env_vars)
    
    # Specific cookies we need
    print("\n" + "=" * 60)
    print("  GITHUB SECRETS TO ADD")
    print("=" * 60)
    if 'cf_clearance' in cookies:
        print(f"CF_CLEARANCE = {cookies['cf_clearance']}")
    if '_ga' in cookies:
        print(f"GA_COOKIE = {cookies['_ga']}")
    if '_ga_ZH4G2KK1JY' in cookies:
        print(f"GA_ZH4G2KK1JY = {cookies['_ga_ZH4G2KK1JY']}")
    
    print("\n" + "=" * 60)
    print("  DONE!")
    print("=" * 60)
    print("\nCopy the values above and add them to GitHub Secrets.")


if __name__ == '__main__':
    main()
