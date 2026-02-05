"""
Scheduler for cloud platforms (Railway, Render, etc.)
Runs scraper on a schedule
"""
import schedule
import time
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_scraper import main

def run_scraper():
    """Wrapper to run scraper and handle errors"""
    try:
        print(f"\n{'='*60}")
        print(f"  Running scheduled scrape at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        main()
        print(f"\n✓ Scrape completed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    except Exception as e:
        print(f"\n✗ Error during scrape: {e}\n")
        import traceback
        traceback.print_exc()

# Run daily at 2 AM UTC
schedule.every().day.at("02:00").do(run_scraper)

# Run immediately on start (for testing/initial run)
print("Running initial scrape...")
run_scraper()

print("\n" + "="*60)
print("  Scheduler started")
print(f"  Next run: {schedule.next_run()}")
print("  Will run daily at 2 AM UTC")
print("="*60 + "\n")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
