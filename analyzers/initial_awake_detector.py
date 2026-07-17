"""
Initial Awake Detector Module
Detects and analyzes initial awake periods before sleep
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple


class InitialAwakeDetector:
    """Detector for initial awake periods"""
    
    def __init__(self, sleep_df: pd.DataFrame):
        self.sleep_df = sleep_df.copy()
        
    def detect_initial_awake(self) -> Dict[str, Any]:
        """Detect initial awake period"""
        if self.sleep_df.empty:
            return {'has_initial_awake': False, 'duration_minutes': 0}
        
        # Sort by timestamp
        if 'timestamp' not in self.sleep_df.columns:
            return {'has_initial_awake': False, 'duration_minutes': 0}
        
        sorted_df = self.sleep_df.sort_values('timestamp').copy()
        
        # Find first sleep record
        sleep_records = sorted_df[sorted_df['is_sleep']]
        
        if sleep_records.empty:
            return {'has_initial_awake': False, 'duration_minutes': 0}
        
        first_sleep_idx = sleep_records.index[0]
        first_sleep_time = sleep_records.loc[first_sleep_idx, 'timestamp']
        
        # Get records before first sleep
        before_sleep = sorted_df.loc[:first_sleep_idx]
        awake_before = before_sleep[~before_sleep['is_sleep']]
        
        if awake_before.empty:
            return {
                'has_initial_awake': False,
                'duration_minutes': 0,
                'sleep_start': str(first_sleep_time)
            }
        
        # Calculate initial awake duration
        duration = self._calculate_duration(awake_before)
        
        return {
            'has_initial_awake': True,
            'duration_records': len(awake_before),
            'duration_minutes': duration,
            'awake_start': str(awake_before['timestamp'].iloc[0]),
            'awake_end': str(awake_before['timestamp'].iloc[-1]),
            'sleep_start': str(first_sleep_time),
            'classification': 'Initial Awake Period Detected'
        }
    
    def _calculate_duration(self, df: pd.DataFrame) -> int:
        """Calculate duration in minutes from records"""
        if len(df) < 2 or 'timestamp' not in df.columns:
            return len(df) * 5  # Assume 5 min intervals
        
        try:
            start = self._parse_timestamp(df['timestamp'].iloc[0])
            end = self._parse_timestamp(df['timestamp'].iloc[-1])
            
            if start and end:
                return int((end - start).total_seconds() / 60)
        except:
            pass
        
        return len(df) * 5
    
    def _parse_timestamp(self, timestamp: str) -> datetime:
        """Parse timestamp"""
        try:
            timestamp = str(timestamp).strip()
            formats = [
                '%Y.%m.%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S',
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp, fmt)
                except ValueError:
                    continue
            return pd.to_datetime(timestamp)
        except:
            return None
    
    def get_sleep_without_initial_awake(self) -> str:
        """Get sleep start time ignoring initial awake"""
        detection = self.detect_initial_awake()
        return detection.get('sleep_start', 'Unknown')
    
    def compare_with_claim(self, claimed_sleep: str) -> Dict[str, Any]:
        """Compare sleep time (with and without initial awake) with user claim"""
        detection = self.detect_initial_awake()
        
        original_start = detection.get('awake_start') if detection['has_initial_awake'] else detection.get('sleep_start')
        ignored_start = detection.get('sleep_start')
        
        return {
            'original_sleep_start': original_start,
            'ignoring_initial_awake': ignored_start,
            'user_claim': claimed_sleep,
            'original_match': self._times_match(original_start, claimed_sleep),
            'ignored_match': self._times_match(ignored_start, claimed_sleep),
            'recommendation': 'Ignore initial awake - matches user claim' if detection['has_initial_awake'] and self._times_match(ignored_start, claimed_sleep) else 'Initial awake analysis inconclusive'
        }
    
    def _times_match(self, time1: str, time2: str, tolerance_minutes: int = 30) -> bool:
        """Check if two times match within tolerance"""
        try:
            minutes1 = self._parse_to_minutes(time1)
            minutes2 = self._parse_to_minutes(time2)
            return abs(minutes1 - minutes2) <= tolerance_minutes
        except:
            return False
    
    def _parse_to_minutes(self, time_str: str) -> int:
        """Parse time to minutes since midnight"""
        try:
            time_str = str(time_str).strip()
            if ' ' in time_str:
                time_part = time_str.split()[-1]
            else:
                time_part = time_str
            
            if ':' in time_part:
                parts = time_part.split(':')
                hours = int(parts[0])
                minutes = int(parts[1]) if len(parts) > 1 else 0
                
                if 'PM' in time_str.upper() and hours != 12:
                    hours += 12
                elif 'AM' in time_str.upper() and hours == 12:
                    hours = 0
                
                return hours * 60 + minutes
            return 0
        except:
            return 0
