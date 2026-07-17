"""
Missing Record Detector Module
Detects gaps in sleep records where ring didn't capture data
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any


class GapDetector:
    """Detector for missing sleep records"""
    
    def __init__(self, sleep_df: pd.DataFrame, expected_interval_minutes: int = 5):
        self.sleep_df = sleep_df.copy()
        self.expected_interval = expected_interval_minutes
        self.gaps = []
        
    def detect_gaps(self) -> List[Dict[str, Any]]:
        """Detect gaps in sleep records"""
        if self.sleep_df.empty or 'timestamp' not in self.sleep_df.columns:
            return []
        
        # Sort by timestamp
        sorted_df = self.sleep_df.sort_values('timestamp').copy()
        
        # Parse timestamps
        sorted_df['parsed_time'] = sorted_df['timestamp'].apply(self._parse_timestamp)
        sorted_df = sorted_df.dropna(subset=['parsed_time'])
        
        if len(sorted_df) < 2:
            return []
        
        # Calculate time differences
        sorted_df['time_diff'] = sorted_df['parsed_time'].diff()
        
        # Find gaps larger than expected interval
        gap_rows = sorted_df[sorted_df['time_diff'] > timedelta(minutes=self.expected_interval)]
        
        self.gaps = []
        for idx, row in gap_rows.iterrows():
            prev_time = sorted_df.loc[idx - 1, 'parsed_time']
            curr_time = row['parsed_time']
            gap_duration = curr_time - prev_time
            
            self.gaps.append({
                'gap_start': str(prev_time),
                'gap_end': str(curr_time),
                'gap_duration_minutes': int(gap_duration.total_seconds() / 60),
                'reason': 'Ring didn\'t capture data',
                'classification': 'Likely Ring Data Loss'
            })
        
        return self.gaps
    
    def _parse_timestamp(self, timestamp: str) -> datetime:
        """Parse various timestamp formats"""
        try:
            timestamp = str(timestamp).strip()
            
            # Try common formats
            formats = [
                '%Y.%m.%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S',
                '%d-%m-%Y %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp, fmt)
                except ValueError:
                    continue
            
            # If all fail, try pandas
            return pd.to_datetime(timestamp)
        except:
            return None
    
    def get_total_missing_time(self) -> int:
        """Get total missing time in minutes"""
        return sum(gap['gap_duration_minutes'] for gap in self.gaps)
    
    def get_gap_summary(self) -> Dict[str, Any]:
        """Get summary of gaps"""
        return {
            'total_gaps': len(self.gaps),
            'total_missing_minutes': self.get_total_missing_time(),
            'gaps': self.gaps,
            'classification': 'Ring Data Loss' if len(self.gaps) > 0 else 'No Gaps Detected'
        }
