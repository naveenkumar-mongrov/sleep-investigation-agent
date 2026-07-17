"""
JSON Parser Module
Parses Ring JSON data and extracts sleep records, heart rate, and other metrics
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd


class JSONParser:
    """Parser for Ring JSON data"""
    
    SLEEP_STAGE_MAPPING = {
        1: "Deep Sleep",
        2: "Light Sleep", 
        3: "REM Sleep"
    }
    
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.data = None
        self.sleep_records = []
        self.heart_rate_data = []
        self.hrv_data = []
        self.activity_data = []
        
    def load_json(self) -> bool:
        """Load and parse JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return False
    
    def extract_sleep_records(self) -> List[Dict[str, Any]]:
        """Extract sleep records from JSON"""
        if not self.data:
            return []
        
        self.sleep_records = []
        
        # Look for sleep data in common locations
        # Try different possible structures based on Ring JSON format
        if 'sleep_data' in self.data:
            sleep_data = self.data['sleep_data']
        elif 'sleep' in self.data:
            sleep_data = self.data['sleep']
        elif 'ring' in self.data and len(self.data['ring']) > 0:
            # Extract from ring array
            ring_data = self.data['ring'][0]
            if 'sleep_data' in ring_data:
                sleep_data = ring_data['sleep_data']
            elif 'sleep' in ring_data:
                sleep_data = ring_data['sleep']
            else:
                sleep_data = []
        else:
            sleep_data = []
        
        # Parse sleep records
        if isinstance(sleep_data, list):
            for record in sleep_data:
                self.sleep_records.append(self._parse_sleep_record(record))
        elif isinstance(sleep_data, dict):
            self.sleep_records.append(self._parse_sleep_record(sleep_data))
        
        return self.sleep_records
    
    def _parse_sleep_record(self, record: Dict) -> Dict[str, Any]:
        """Parse individual sleep record"""
        parsed = {
            'timestamp': record.get('timestamp') or record.get('time') or record.get('date'),
            'stage': record.get('stage') or record.get('sleep_stage') or record.get('level'),
            'heart_rate': record.get('heart_rate') or record.get('hr') or record.get('bpm'),
            'hrv': record.get('hrv') or record.get('heart_rate_variability'),
            'movement': record.get('movement') or record.get('activity') or record.get('steps'),
            'spo2': record.get('spo2') or record.get('oxygen'),
            'temperature': record.get('temperature') or record.get('temp')
        }
        return parsed
    
    def extract_heart_rate(self) -> List[Dict[str, Any]]:
        """Extract heart rate data"""
        if not self.data:
            return []
        
        self.heart_rate_data = []
        
        # Look for heart rate data
        if 'heart_rate' in self.data:
            hr_data = self.data['heart_rate']
        elif 'heartRate' in self.data:
            hr_data = self.data['heartRate']
        elif 'hr' in self.data:
            hr_data = self.data['hr']
        elif 'ring' in self.data and len(self.data['ring']) > 0:
            ring_data = self.data['ring'][0]
            if 'heart_rate' in ring_data:
                hr_data = ring_data['heart_rate']
            elif 'heartRate' in ring_data:
                hr_data = ring_data['heartRate']
            else:
                hr_data = []
        else:
            hr_data = []
        
        # Parse heart rate records
        if isinstance(hr_data, list):
            for record in hr_data:
                self.heart_rate_data.append({
                    'timestamp': record.get('timestamp') or record.get('time'),
                    'value': record.get('value') or record.get('bpm') or record.get('hr')
                })
        
        return self.heart_rate_data
    
    def extract_activity(self) -> List[Dict[str, Any]]:
        """Extract activity data"""
        if not self.data:
            return []
        
        self.activity_data = []
        
        if 'activitydetails' in self.data:
            activity_data = self.data['activitydetails']
        elif 'activity' in self.data:
            activity_data = self.data['activity']
        else:
            activity_data = []
        
        if isinstance(activity_data, list):
            for record in activity_data:
                self.activity_data.append({
                    'timestamp': record.get('date'),
                    'steps': record.get('step'),
                    'calories': record.get('calories'),
                    'distance': record.get('distance')
                })
        
        return self.activity_data
    
    def get_sleep_stages(self) -> pd.DataFrame:
        """Convert sleep records to DataFrame with stage classification"""
        if not self.sleep_records:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.sleep_records)
        
        # Classify sleep stages
        def classify_stage(stage):
            if stage in self.SLEEP_STAGE_MAPPING:
                return self.SLEEP_STAGE_MAPPING[stage]
            return "Awake"
        
        df['stage_classified'] = df['stage'].apply(classify_stage)
        df['is_sleep'] = df['stage'].isin(self.SLEEP_STAGE_MAPPING.keys())
        
        return df
    
    def get_heart_rate_df(self) -> pd.DataFrame:
        """Convert heart rate data to DataFrame"""
        if not self.heart_rate_data:
            return pd.DataFrame()
        
        return pd.DataFrame(self.heart_rate_data)
    
    def parse_all(self) -> Dict[str, Any]:
        """Parse all data from JSON"""
        self.load_json()
        self.extract_sleep_records()
        self.extract_heart_rate()
        self.extract_activity()
        
        return {
            'sleep_records': self.get_sleep_stages(),
            'heart_rate': self.get_heart_rate_df(),
            'activity': pd.DataFrame(self.activity_data),
            'raw_sleep': self.sleep_records,
            'raw_heart_rate': self.heart_rate_data,
            'raw_activity': self.activity_data
        }
