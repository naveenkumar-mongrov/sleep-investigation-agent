"""
Configuration file for Sleep Investigation Agent
"""

import os

# OpenAI API Key - Set as environment variable in Streamlit Cloud
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Google Sheets API Key - Set as environment variable in Streamlit Cloud
GOOGLE_SHEETS_API_KEY = os.environ.get("GOOGLE_SHEETS_API_KEY", "")

# GitHub Token (for private repositories) - Set as environment variable in Streamlit Cloud
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Batch processing settings
MAX_WORKERS = 4  # Number of parallel workers for batch processing

# External data source configuration
GOOGLE_SHEETS_ID = "1-1-YXzZUF_Flsb8hWy_9ubvYvkXRSGB1N2OWtKdUt8s"  # Spreadsheet ID from Google Sheets URL
GOOGLE_SHEETS_SHEET_NAME = "Sheet1"  # Sheet name to fetch from

GITHUB_OWNER = "mongrov"  # GitHub repository owner
GITHUB_REPO = "ziva_app"  # GitHub repository name
GITHUB_PATH = "fix/sleepProcessed/packages/ux/helpers/testFiles"  # Path to JSON files in repository
