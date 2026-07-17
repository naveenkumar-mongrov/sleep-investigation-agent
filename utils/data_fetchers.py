"""
Data Fetchers Module
Integrations for fetching data from external sources (Google Sheets, GitHub)
"""

import os
import requests
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from io import StringIO


class GoogleSheetsFetcher:
    """Fetcher for Google Sheets data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://sheets.googleapis.com/v4/spreadsheets"
    
    def fetch_sheet_data(
        self,
        spreadsheet_id: str,
        sheet_name: str = "Sheet1",
        range: str = "A1:Z1000"
    ) -> List[Dict[str, Any]]:
        """Fetch data from Google Sheets"""
        if not self.api_key:
            raise ValueError("Google Sheets API key is required")
        
        url = f"{self.base_url}/{spreadsheet_id}/values/{sheet_name}!{range}?key={self.api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            values = data.get('values', [])
            
            if not values:
                return []
            
            # Convert to list of dictionaries
            headers = values[0]
            rows = values[1:]
            
            result = []
            for row in rows:
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = row[i] if i < len(row) else ""
                result.append(row_dict)
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to fetch Google Sheets data: {str(e)}")
    
    def fetch_sheet_as_dataframe(
        self,
        spreadsheet_id: str,
        sheet_name: str = "Sheet1",
        range: str = "A1:Z1000"
    ) -> pd.DataFrame:
        """Fetch Google Sheets data as DataFrame"""
        data = self.fetch_sheet_data(spreadsheet_id, sheet_name, range)
        return pd.DataFrame(data)
    
    def convert_to_claims_format(
        self,
        sheet_data: List[Dict[str, Any]],
        column_mapping: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Convert Google Sheets data to claims format"""
        claims = []
        
        for row in sheet_data:
            claim = {
                "filename": row.get(column_mapping.get('filename', 'filename'), ''),
                "user_id": row.get(column_mapping.get('user_id', 'user_id'), ''),
                "sleep_start": row.get(column_mapping.get('sleep_start', 'sleep_start'), ''),
                "wake_time": row.get(column_mapping.get('wake_time', 'wake_time'), ''),
                "awake_during": row.get(column_mapping.get('awake_during', 'awake_during'), ''),
                "nap": row.get(column_mapping.get('nap', 'nap'), ''),
                "remarks": row.get(column_mapping.get('remarks', 'remarks'), ''),
                "production_data": {
                    "sleep_start": row.get(column_mapping.get('prod_sleep_start', 'prod_sleep_start'), ''),
                    "sleep_end": row.get(column_mapping.get('prod_sleep_end', 'prod_sleep_end'), ''),
                    "deep": row.get(column_mapping.get('prod_deep', 'prod_deep'), ''),
                    "light": row.get(column_mapping.get('prod_light', 'prod_light'), ''),
                    "rem": row.get(column_mapping.get('prod_rem', 'prod_rem'), ''),
                    "awake": row.get(column_mapping.get('prod_awake', 'prod_awake'), '')
                },
                "test_data": {
                    "sleep_start": row.get(column_mapping.get('test_sleep_start', 'test_sleep_start'), ''),
                    "sleep_end": row.get(column_mapping.get('test_sleep_end', 'test_sleep_end'), ''),
                    "deep": row.get(column_mapping.get('test_deep', 'test_deep'), ''),
                    "light": row.get(column_mapping.get('test_light', 'test_light'), ''),
                    "rem": row.get(column_mapping.get('test_rem', 'test_rem'), ''),
                    "awake": row.get(column_mapping.get('test_awake', 'test_awake'), '')
                }
            }
            claims.append(claim)
        
        return claims


class GitHubFetcher:
    """Fetcher for GitHub repository files"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {}
        if self.token:
            self.headers['Authorization'] = f"token {self.token}"
    
    def fetch_repository_files(
        self,
        owner: str,
        repo: str,
        path: str = "",
        file_extension: str = ".json"
    ) -> List[Dict[str, Any]]:
        """Fetch all files with specified extension from repository"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, dict) and data.get('type') == 'file':
                # Single file
                return [data]
            
            # Directory - fetch all files
            files = []
            if isinstance(data, list):
                for item in data:
                    if item.get('type') == 'file' and item.get('name', '').endswith(file_extension):
                        files.append(item)
                    elif item.get('type') == 'dir':
                        # Recursively fetch subdirectories
                        sub_files = self.fetch_repository_files(
                            owner, repo, 
                            f"{path}/{item['name']}" if path else item['name'],
                            file_extension
                        )
                        files.extend(sub_files)
            
            return files
            
        except Exception as e:
            raise Exception(f"Failed to fetch GitHub repository files: {str(e)}")
    
    def fetch_file_content(self, download_url: str) -> str:
        """Fetch file content from download URL"""
        try:
            response = requests.get(download_url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Failed to fetch file content: {str(e)}")
    
    def fetch_json_files(
        self,
        owner: str,
        repo: str,
        path: str = "",
        save_dir: str = "uploads/github"
    ) -> List[str]:
        """Fetch all JSON files from repository and save locally"""
        os.makedirs(save_dir, exist_ok=True)
        
        files = self.fetch_repository_files(owner, repo, path, ".json")
        saved_paths = []
        
        for file_info in files:
            try:
                content = self.fetch_file_content(file_info['download_url'])
                
                # Save file locally
                filename = file_info['name']
                filepath = os.path.join(save_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                saved_paths.append(filepath)
                
            except Exception as e:
                print(f"Failed to fetch {file_info['name']}: {str(e)}")
        
        return saved_paths
    
    def fetch_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository information"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch repository info: {str(e)}")


class DataIntegrator:
    """Integrator for combining data from multiple sources"""
    
    def __init__(
        self,
        google_sheets_api_key: Optional[str] = None,
        github_token: Optional[str] = None
    ):
        self.sheets_fetcher = GoogleSheetsFetcher(google_sheets_api_key)
        self.github_fetcher = GitHubFetcher(github_token)
    
    def fetch_batch_data(
        self,
        google_sheets_id: Optional[str] = None,
        github_owner: Optional[str] = None,
        github_repo: Optional[str] = None,
        github_path: str = "",
        sheet_name: str = "Sheet1",
        column_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Fetch data from both Google Sheets and GitHub"""
        
        result = {
            'claims': [],
            'json_files': [],
            'errors': []
        }
        
        # Fetch from Google Sheets
        if google_sheets_id:
            try:
                sheet_data = self.sheets_fetcher.fetch_sheet_data(
                    google_sheets_id,
                    sheet_name
                )
                
                if column_mapping:
                    result['claims'] = self.sheets_fetcher.convert_to_claims_format(
                        sheet_data,
                        column_mapping
                    )
                else:
                    # Use default column mapping
                    default_mapping = {
                        'filename': 'filename',
                        'user_id': 'user_id',
                        'sleep_start': 'sleep_start',
                        'wake_time': 'wake_time',
                        'awake_during': 'awake_during',
                        'nap': 'nap',
                        'remarks': 'remarks',
                        'prod_sleep_start': 'prod_sleep_start',
                        'prod_sleep_end': 'prod_sleep_end',
                        'prod_deep': 'prod_deep',
                        'prod_light': 'prod_light',
                        'prod_rem': 'prod_rem',
                        'prod_awake': 'prod_awake',
                        'test_sleep_start': 'test_sleep_start',
                        'test_sleep_end': 'test_sleep_end',
                        'test_deep': 'test_deep',
                        'test_light': 'test_light',
                        'test_rem': 'test_rem',
                        'test_awake': 'test_awake'
                    }
                    result['claims'] = self.sheets_fetcher.convert_to_claims_format(
                        sheet_data,
                        default_mapping
                    )
                
                result['sheet_data'] = sheet_data
                
            except Exception as e:
                result['errors'].append(f"Google Sheets error: {str(e)}")
        
        # Fetch from GitHub
        if github_owner and github_repo:
            try:
                json_files = self.github_fetcher.fetch_json_files(
                    github_owner,
                    github_repo,
                    github_path
                )
                result['json_files'] = json_files
                
                # Fetch repository info
                repo_info = self.github_fetcher.fetch_repository_info(
                    github_owner,
                    github_repo
                )
                result['repo_info'] = repo_info
                
            except Exception as e:
                result['errors'].append(f"GitHub error: {str(e)}")
        
        return result
