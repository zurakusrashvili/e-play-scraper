"""
Automated cookie fetcher using Playwright
Gets fresh cookies from e-play.pl automatically
"""
import json
import os
import time
from playwright.sync_api import sync_playwright


def get_fresh_cookies():
    """Get fresh cookies from e-play.pl using headless browser"""
    print("Getting fresh cookies from e-play.pl...")
    
    with sync_playwright() as p:
        # Launch browser (headless)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            # Navigate to the page (this will trigger Cloudflare if needed)
            print("Navigating to e-play.pl...")
            page.goto('https://e-play.pl/umowy/', wait_until='networkidle', timeout=60000)
            
            # Wait a bit for any JavaScript/Cloudflare challenges
            time.sleep(3)
            
            # Get cookies
            cookies = context.cookies()
            cookie_dict = {}
            
            for cookie in cookies:
                cookie_dict[cookie['name']] = cookie['value']
            
            browser.close()
            
            # Check if we got the important cookie
            if 'cf_clearance' not in cookie_dict:
                print("⚠️  WARNING: cf_clearance cookie not found!")
                print("   Cloudflare challenge may not have been solved.")
                print("   Cookies retrieved:", list(cookie_dict.keys()))
            else:
                print(f"✓ Successfully retrieved {len(cookie_dict)} cookies")
                print(f"  - cf_clearance: {cookie_dict['cf_clearance'][:50]}...")
            
            return cookie_dict
            
        except Exception as e:
            print(f"✗ Error getting cookies: {e}")
            browser.close()
            return None


def save_cookies_to_env_file(cookies, env_file='.env.cookies'):
    """Save cookies to .env file format"""
    if not cookies:
        return False
    
    lines = []
    lines.append("# Auto-generated cookies - DO NOT COMMIT TO GIT")
    lines.append(f"CF_CLEARANCE={cookies.get('cf_clearance', '')}")
    if '_ga' in cookies:
        lines.append(f"GA_COOKIE={cookies.get('_ga', '')}")
    if '_ga_ZH4G2KK1JY' in cookies:
        lines.append(f"GA_ZH4G2KK1JY={cookies.get('_ga_ZH4G2KK1JY', '')}")
    
    with open(env_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Saved cookies to {env_file}")
    return True


def main():
    """Main function"""
    cookies = get_fresh_cookies()
    
    if cookies:
        # Save to .env file
        save_cookies_to_env_file(cookies)
        
        # Print for GitHub Secrets
        print("\n" + "="*60)
        print("  GITHUB SECRETS (copy these values)")
        print("="*60)
        if 'cf_clearance' in cookies:
            print(f"CF_CLEARANCE={cookies['cf_clearance']}")
        if '_ga' in cookies:
            print(f"GA_COOKIE={cookies['_ga']}")
        if '_ga_ZH4G2KK1JY' in cookies:
            print(f"GA_ZH4G2KK1JY={cookies['_ga_ZH4G2KK1JY']}")
        print("="*60)
        
        return cookies
    else:
        print("✗ Failed to get cookies")
        return None


if __name__ == '__main__':
    main()
