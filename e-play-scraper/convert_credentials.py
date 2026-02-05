"""
Helper script to convert credentials.json to string format for GitHub Secrets
"""
import json
import sys
import os

def convert_credentials():
    """Convert credentials.json to JSON string for GitHub Secrets"""
    credentials_file = 'credentials.json'
    
    if not os.path.exists(credentials_file):
        print(f"ERROR: {credentials_file} not found!")
        print("\nMake sure credentials.json is in the same folder as this script.")
        return
    
    try:
        # Read and parse JSON
        with open(credentials_file, 'r', encoding='utf-8') as f:
            creds = json.load(f)
        
        # Convert to compact JSON string
        json_string = json.dumps(creds, separators=(',', ':'))
        
        print("=" * 60)
        print("  CREDENTIALS JSON STRING (for GitHub Secret)")
        print("=" * 60)
        print("\nCopy this entire string:")
        print("-" * 60)
        print(json_string)
        print("-" * 60)
        print(f"\nLength: {len(json_string)} characters")
        print("\nNext steps:")
        print("1. Copy the string above (Ctrl+A, Ctrl+C)")
        print("2. Go to GitHub → Settings → Secrets → New secret")
        print("3. Name: SHEETS_CREDENTIALS_JSON")
        print("4. Paste the string → Add secret")
        print("=" * 60)
        
        # Try to copy to clipboard (Windows)
        try:
            import pyperclip
            pyperclip.copy(json_string)
            print("\n✓ Copied to clipboard! Just paste it in GitHub.")
        except ImportError:
            print("\n💡 Tip: Install pyperclip to auto-copy:")
            print("   pip install pyperclip")
        except Exception:
            pass  # Clipboard not available, that's okay
        
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {credentials_file}")
        print(f"Details: {e}")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == '__main__':
    convert_credentials()
