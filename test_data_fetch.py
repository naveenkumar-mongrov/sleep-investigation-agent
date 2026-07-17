"""
Test script to verify data fetching from external sources
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_fetchers import GoogleSheetsFetcher, GitHubFetcher, DataIntegrator
import config

print("Testing Data Fetching...")
print("=" * 50)

# Test Google Sheets
print("\n1. Testing Google Sheets Fetch...")
try:
    sheets_fetcher = GoogleSheetsFetcher(config.GOOGLE_SHEETS_API_KEY)
    sheet_data = sheets_fetcher.fetch_sheet_data(
        config.GOOGLE_SHEETS_ID,
        config.GOOGLE_SHEETS_SHEET_NAME
    )
    print(f"✓ Successfully fetched {len(sheet_data)} rows from Google Sheets")
    if sheet_data:
        print(f"  Sample row keys: {list(sheet_data[0].keys())}")
except Exception as e:
    print(f"✗ Google Sheets error: {str(e)}")

# Test GitHub
print("\n2. Testing GitHub Fetch...")
try:
    github_fetcher = GitHubFetcher(config.GITHUB_TOKEN)
    files = github_fetcher.fetch_repository_files(
        config.GITHUB_OWNER,
        config.GITHUB_REPO,
        config.GITHUB_PATH,
        ".json"
    )
    print(f"✓ Successfully found {len(files)} JSON files in GitHub")
    if files:
        print(f"  Sample file: {files[0]['name']}")
except Exception as e:
    print(f"✗ GitHub error: {str(e)}")

# Test Combined
print("\n3. Testing Combined Data Fetch...")
try:
    integrator = DataIntegrator(config.GOOGLE_SHEETS_API_KEY, config.GITHUB_TOKEN)
    data = integrator.fetch_batch_data(
        google_sheets_id=config.GOOGLE_SHEETS_ID,
        github_owner=config.GITHUB_OWNER,
        github_repo=config.GITHUB_REPO,
        github_path=config.GITHUB_PATH,
        sheet_name=config.GOOGLE_SHEETS_SHEET_NAME
    )
    print(f"✓ Combined fetch successful")
    print(f"  Claims: {len(data.get('claims', []))}")
    print(f"  JSON files: {len(data.get('json_files', []))}")
    if data.get('errors'):
        print(f"  Errors: {data['errors']}")
except Exception as e:
    print(f"✗ Combined fetch error: {str(e)}")

print("\n" + "=" * 50)
print("Test completed!")
