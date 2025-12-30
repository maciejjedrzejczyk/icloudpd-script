#!/usr/bin/env python3
import subprocess
import sys
import argparse
import os
from pathlib import Path

# Load credentials from .env file
def load_env():
    env_file = Path(__file__).parent / '.env'
    env_vars = {}
    
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars

env = load_env()
USERNAME = env.get('ICLOUD_USERNAME', '')
PASSWORD = env.get('ICLOUD_PASSWORD', '')
TIMEZONE = env.get('TIMEZONE', 'Europe/London')
DOWNLOAD_SIZE = env.get('DOWNLOAD_SIZE', 'original')
DATA_DIR = env.get('DATA_DIR', './icloud-photos')
COOKIES_DIR = env.get('COOKIES_DIR', './icloudpd-cookies')

if not USERNAME or not PASSWORD:
    print("Error: ICLOUD_USERNAME and ICLOUD_PASSWORD must be set in .env file")
    sys.exit(1)

def get_albums():
    """Fetch list of albums from iCloud"""
    print("Fetching album list...")
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{COOKIES_DIR}:/cookies",
        "-e", f"TZ={TIMEZONE}",
        "icloudpd/icloudpd:latest",
        "icloudpd",
        "--cookie-directory", "/cookies",
        "--username", USERNAME,
        "--password", PASSWORD,
        "--list-albums"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Extract album names from output
    lines = result.stdout.split('\n')
    albums = []
    capture = False
    
    for line in lines:
        if line.strip() == "Albums:":
            capture = True
            continue
        if capture and line.strip():
            albums.append(line.strip())
    
    return albums

def download_album(album):
    """Download a specific album"""
    print(f"\nDownloading album: {album}")
    # Create safe container name by removing non-ASCII characters
    safe_name = ''.join(c if c.isalnum() or c in '-_.' else '-' for c in album.encode('ascii', 'ignore').decode())
    
    cmd = [
        "docker", "run", "--rm",
        "--name", f"icloudpd-album-{safe_name}",
        "-v", f"{DATA_DIR}:/data",
        "-v", f"{COOKIES_DIR}:/cookies",
        "-e", f"TZ={TIMEZONE}",
        "icloudpd/icloudpd:latest",
        "icloudpd",
        "--directory", f"/data/albums/{album}",
        "--cookie-directory", "/cookies",
        "--folder-structure", "{:%Y/%Y-%m-%d}",
        "--username", USERNAME,
        "--password", PASSWORD,
        "--size", DOWNLOAD_SIZE,
        "--album", album
    ]
    
    subprocess.run(cmd)

def download_by_date_range(start_date, end_date):
    """Download photos by date range"""
    print(f"\nDownloading photos from {start_date} to {end_date}")
    cmd = [
        "docker", "run", "--rm",
        "--name", "icloudpd-extract-range",
        "-v", f"{DATA_DIR}:/data",
        "-v", f"{COOKIES_DIR}:/cookies",
        "-e", f"TZ={TIMEZONE}",
        "icloudpd/icloudpd:latest",
        "icloudpd",
        "--directory", "/data",
        "--cookie-directory", "/cookies",
        "--folder-structure", "{:%Y/%Y-%m-%d}",
        "--username", USERNAME,
        "--password", PASSWORD,
        "--size", DOWNLOAD_SIZE,
        "--skip-created-before", start_date,
        "--skip-created-after", end_date,
        "--auto-delete"
    ]
    
    subprocess.run(cmd)

def download_all():
    """Download all photos"""
    print("\nDownloading all photos from iCloud...")
    cmd = [
        "docker", "run", "--rm",
        "--name", "icloudpd-extract-all",
        "-v", f"{DATA_DIR}:/data",
        "-v", f"{COOKIES_DIR}:/cookies",
        "-e", f"TZ={TIMEZONE}",
        "icloudpd/icloudpd:latest",
        "icloudpd",
        "--directory", "/data",
        "--cookie-directory", "/cookies",
        "--folder-structure", "{:%Y/%Y-%m-%d}",
        "--username", USERNAME,
        "--password", PASSWORD,
        "--size", DOWNLOAD_SIZE,
        "--recent", "500000",
        "--auto-delete"
    ]
    
    subprocess.run(cmd)

def reload_credentials():
    """Reload iCloud credentials interactively"""
    print("\nReloading iCloud credentials (interactive mode for 2FA)...")
    cmd = [
        "docker", "run", "-it",
        "--name", "icloudpd-reload-creds",
        "-v", f"{DATA_DIR}:/data",
        "-v", f"{COOKIES_DIR}:/cookies",
        "-e", f"TZ={TIMEZONE}",
        "icloudpd/icloudpd:latest",
        "icloudpd",
        "--directory", "/data",
        "--cookie-directory", "/cookies",
        "--folder-structure", "{:%Y/%Y-%m-%d}",
        "--username", USERNAME,
        "--password", PASSWORD,
        "--size", DOWNLOAD_SIZE,
        "--recent", "1"
    ]
    
    subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(description='Download photos from iCloud by albums or date range')
    parser.add_argument('--mode', choices=['albums', 'date', 'reload', 'all'], help='Mode: albums, date range, reload credentials, or download all')
    parser.add_argument('--start-date', help='Start date for date range mode (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date for date range mode (YYYY-MM-DD)')
    args = parser.parse_args()
    
    # Determine mode
    if args.mode:
        mode = args.mode
    else:
        print("Select mode:")
        print("1. Download by albums")
        print("2. Download by date range")
        print("3. Reload iCloud credentials")
        print("4. Download all photos")
        choice = input("\nEnter choice (1, 2, 3, or 4): ").strip()
        mode = 'albums' if choice == '1' else ('date' if choice == '2' else ('reload' if choice == '3' else 'all'))
    
    if mode == 'reload':
        reload_credentials()
        print("\nDone!")
        return
    
    if mode == 'all':
        download_all()
        print("\nDone!")
        return
    
    if mode == 'date':
        # Date range mode
        if args.start_date and args.end_date:
            start_date = args.start_date
            end_date = args.end_date
        else:
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
        
        download_by_date_range(start_date, end_date)
        print("\nDone!")
        return
    
    # Albums mode
    albums = get_albums()
    
    if not albums:
        print("No albums found or authentication failed")
        sys.exit(1)
    
    print(f"\nFound {len(albums)} albums:\n")
    for i, album in enumerate(albums, 1):
        print(f"{i}. {album}")
    
    print("\nSelect albums to download:")
    print("  - Enter numbers or names separated by commas (e.g., 1,3,5 or beks,AWS)")
    print("  - Enter 'all' to download all albums")
    print("  - Enter 'none' or press Enter to abort")
    
    selection = input("\nYour selection: ").strip()
    
    if not selection or selection.lower() == 'none':
        print("\nNo albums selected. Exiting.")
        sys.exit(0)
    
    selected = []
    
    if selection.lower() == 'all':
        selected = albums
    else:
        # Parse selection
        parts = [p.strip() for p in selection.split(',')]
        for part in parts:
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(albums):
                    selected.append(albums[idx])
            else:
                # Try to match by name
                for album in albums:
                    if part.lower() in album.lower():
                        selected.append(album)
                        break
    
    if not selected:
        print("\nNo valid albums selected. Exiting.")
        sys.exit(0)
    
    print(f"\n{len(selected)} album(s) selected:")
    for album in selected:
        print(f"  - {album}")
    
    confirm = input("\nProceed with download? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\nAborted.")
        sys.exit(0)
    
    print("\nStarting downloads...\n")
    
    for album in selected:
        download_album(album)
    
    print("\nDone!")

if __name__ == "__main__":
    main()
