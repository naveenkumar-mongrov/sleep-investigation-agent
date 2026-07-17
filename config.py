"""
Configuration file for Sleep Investigation Agent
"""

# OpenAI API Key
OPENAI_API_KEY = "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"

# Google Sheets API Key
GOOGLE_SHEETS_API_KEY = "407410313777-dp0agbnlgd173nta01g3hfubt9s3ovn0.apps.googleusercontent.com"  # Add your Google Sheets API key here

# GitHub Token (for private repositories)
GITHUB_TOKEN = ""  # Add your GitHub personal access token here

# Batch processing settings
MAX_WORKERS = 4  # Number of parallel workers for batch processing

# External data source configuration
GOOGLE_SHEETS_ID = "1-1-YXzZUF_Flsb8hWy_9ubvYvkXRSGB1N2OWtKdUt8s"  # Spreadsheet ID from Google Sheets URL
GOOGLE_SHEETS_SHEET_NAME = "Sheet1"  # Sheet name to fetch from

GITHUB_OWNER = "mongrov"  # GitHub repository owner
GITHUB_REPO = "ziva_app"  # GitHub repository name
GITHUB_PATH = "fix/sleepProcessed/packages/ux/helpers/testFiles"  # Path to JSON files in repository
