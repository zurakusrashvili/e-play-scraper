"""
Get cookies by making API request through browser
This ensures cookies are valid for the API endpoint
"""
import json
import os
import time
from playwright.sync_api import sync_playwright


def get_cookies_via_api():
    """Get cookies by making API request through browser"""
    print("Getting cookies via browser API request...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Hide automation
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
        """)
        
        page = context.new_page()
        
        try:
            # First, visit the main page to get initial cookies
            print("Visiting e-play.pl...")
            page.goto('https://e-play.pl/umowy/', wait_until='domcontentloaded', timeout=60000)
            time.sleep(5)  # Wait for Cloudflare
            
            # Now make API request through browser (this ensures cookies work for API)
            print("Making API request through browser...")
            api_result = page.evaluate("""
                async () => {
                    try {
                        const response = await fetch('https://e-play.pl/wp-json/contracts/v1/filter', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Accept': '*/*',
                                'Origin': 'https://e-play.pl',
                                'Referer': 'https://e-play.pl/umowy/'
                            },
                            body: JSON.stringify({paged: 1, quantity: 1})
                        });
                        
                        if (response.ok) {
                            const data = await response.json();
                            return { status: response.status, success: true, itemCount: data.items?.length || 0 };
                        } else {
                            return { status: response.status, success: false, error: 'API request failed' };
                        }
                    } catch (error) {
                        return { status: 0, success: false, error: error.message };
                    }
                }
            """)
            
            print(f"API test result: {api_result}")
            
            if not api_result.get('success'):
                print(f"⚠️  API request failed: {api_result}")
                print("Cookies may not be valid for API endpoint")
            
            # Get cookies after API request
            cookies = context.cookies()
            cookie_dict = {}
            
            for cookie in cookies:
                cookie_dict[cookie['name']] = cookie['value']
            
            browser.close()
            
            if 'cf_clearance' not in cookie_dict:
                print("⚠️  WARNING: cf_clearance cookie not found!")
                return None
            
            print(f"✓ Retrieved {len(cookie_dict)} cookies")
            print(f"  - cf_clearance: {cookie_dict['cf_clearance'][:50]}...")
            
            return cookie_dict
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            browser.close()
            return None


def save_cookies_to_env_file(cookies, env_file='.env.cookies'):
    """Save cookies to .env file format"""
    if not cookies:
        return False
    
    lines = []
    lines.append("# Auto-generated cookies")
    lines.append(f"CF_CLEARANCE={cookies.get('cf_clearance', '')}")
    if '_ga' in cookies:
        lines.append(f"GA_COOKIE={cookies.get('_ga', '')}")
    if '_ga_ZH4G2KK1JY' in cookies:
        lines.append(f"GA_ZH4G2KK1JY={cookies.get('_ga_ZH4G2KK1JY', '')}")
    
    with open(env_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Saved cookies to {env_file}")
    return True


if __name__ == '__main__':
    cookies = get_cookies_via_api()
    if cookies:
        save_cookies_to_env_file(cookies)
        print("\n✓ Cookies ready for use!")
