"""
Sleep Analyzer Module
Analyzes sleep records, calculates sleep metrics, and maps sleep stages
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple


class SleepAnalyzer:
    """Analyzer for sleep data"""
    
    SLEEP_STAGE_MAPPING = {
        1: "Deep Sleep",
        2: "Light Sleep",
        3: "REM Sleep"
    }
    
    def __init__(self, sleep_df: pd.DataFrame):
        self.sleep_df = sleep_df.copy()
        self.analysis_results = {}
        
    def analyze_sleep_periods(self) -> Dict[str, Any]:
        """Analyze sleep periods and calculate metrics"""
        if self.sleep_df.empty:
            return {'error': 'No sleep data available'}
        
        # Filter only sleep records (stages 1, 2, 3)
        sleep_only = self.sleep_df[self.sleep_df['is_sleep']].copy()
        awake_only = self.sleep_df[~self.sleep_df['is_sleep']].copy()
        
        if sleep_only.empty:
            return {'error': 'No sleep records found'}
        
        # Calculate sleep metrics
        results = {
            'total_sleep_records': len(sleep_only),
            'total_awake_records': len(awake_only),
            'sleep_start': self._get_sleep_start(sleep_only),
            'sleep_end': self._get_sleep_end(sleep_only),
            'stage_distribution': self._calculate_stage_distribution(sleep_only),
            'awake_periods': self._identify_awake_periods(awake_only),
            'sleep_efficiency': self._calculate_sleep_efficiency(sleep_only, awake_only)
        }
        
        self.analysis_results = results
        return results
    
    def _get_sleep_start(self, sleep_df: pd.DataFrame) -> str:
        """Get sleep start time"""
        if 'timestamp' in sleep_df.columns:
            return str(sleep_df['timestamp'].min())
        return "Unknown"
    
    def _get_sleep_end(self, sleep_df: pd.DataFrame) -> str:
        """Get sleep end time"""
        if 'timestamp' in sleep_df.columns:
            return str(sleep_df['timestamp'].max())
        return "Unknown"
    
    def _calculate_stage_distribution(self, sleep_df: pd.DataFrame) -> Dict[str, int]:
        """Calculate distribution of sleep stages"""
        if 'stage_classified' in sleep_df.columns:
            return sleep_df['stage_classified'].value_counts().to_dict()
        
        # Fallback to raw stage
        if 'stage' in sleep_df.columns:
            distribution = {}
            for stage, name in self.SLEEP_STAGE_MAPPING.items():
                count = len(sleep_df[sleep_df['stage'] == stage])
                if count > 0:
                    distribution[name] = count
            return distribution
        
        return {}
    
    def _identify_awake_periods(self, awake_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify awake periods during sleep"""
        if awake_df.empty:
            return []
        
        awake_periods = []
        if 'timestamp' in awake_df.columns:
            for _, row in awake_df.iterrows():
                awake_periods.append({
                    'timestamp': str(row['timestamp']),
                    'duration': row.get('duration', 0)
                })
        
        return awake_periods
    
    def _calculate_sleep_efficiency(self, sleep_df: pd.DataFrame, awake_df: pd.DataFrame) -> float:
        """Calculate sleep efficiency"""
        total_records = len(sleep_df) + len(awake_df)
        if total_records == 0:
            return 0.0
        
        return (len(sleep_df) / total_records) * 100
    
    def get_initial_awake_duration(self) -> Tuple[str, int]:
        """Get initial awake period duration before first sleep"""
        if self.sleep_df.empty:
            return "Unknown", 0
        
        # Sort by timestamp
        if 'timestamp' in self.sleep_df.columns:
            sorted_df = self.sleep_df.sort_values('timestamp')
            
            # Find first sleep record
            first_sleep = sorted_df[sorted_df['is_sleep']].first_valid_index()
            
            if first_sleep is not None:
                # Get awake records before first sleep
                awake_before = sorted_df.loc[:first_sleep]
                awake_before = awake_before[~awake_before['is_sleep']]
                
                if not awake_before.empty:
                    return str(awake_before['timestamp'].iloc[-1]), len(awake_before)
        
        return "None", 0
    
    def ignore_initial_awake(self) -> Dict[str, Any]:
        """Calculate sleep metrics ignoring initial awake period"""
        if self.sleep_df.empty:
            return {'error': 'No sleep data available'}
        
        # Get initial awake info
        initial_awake_end, initial_awake_count = self.get_initial_awake_duration()
        
        # Filter out initial awake
        if initial_awake_count > 0 and 'timestamp' in self.sleep_df.columns:
            filtered_df = self.sleep_df[self.sleep_df['timestamp'] > initial_awake_end].copy()
        else:
            filtered_df = self.sleep_df.copy()
        
        # Re-analyze with filtered data
        temp_analyzer = SleepAnalyzer(filtered_df)
        results = temp_analyzer.analyze_sleep_periods()
        results['initial_awake_removed'] = initial_awake_count
        results['initial_awake_end_time'] = initial_awake_end
        
        return results
    
    def compare_with_claim(self, claimed_sleep_start: str, claimed_wake_time: str) -> Dict[str, Any]:
        """Compare JSON sleep data with user claim"""
        results = self.analyze_sleep_periods()
        
        comparison = {
            'claimed_sleep_start': claimed_sleep_start,
            'claimed_wake_time': claimed_wake_time,
            'json_sleep_start': results.get('sleep_start', 'Unknown'),
            'json_sleep_end': results.get('sleep_end', 'Unknown'),
            'start_match': self._compare_times(claimed_sleep_start, results.get('sleep_start')),
            'end_match': self._compare_times(claimed_wake_time, results.get('sleep_end'))
        }
        
        # Also check with initial awake ignored
        ignored_results = self.ignore_initial_awake()
        comparison['json_sleep_start_ignored'] = ignored_results.get('sleep_start', 'Unknown')
        comparison['start_match_ignored'] = self._compare_times(
            claimed_sleep_start, 
            ignored_results.get('sleep_start')
        )
        
        return comparison
    
    def _compare_times(self, time1: str, time2: str, tolerance_minutes: int = 30) -> bool:
        """Compare two times with tolerance"""
        try:
            # Simple string comparison for now
            # In production, parse and compare with tolerance
            return abs(self._parse_time_to_minutes(time1) - self._parse_time_to_minutes(time2)) <= tolerance_minutes
        except:
            return False
    
    def _parse_time_to_minutes(self, time_str: str) -> int:
        """Parse time string to minutes since midnight"""
        try:
            # Handle various time formats
            time_str = str(time_str).strip()
            
            # Try to extract time portion
            if ' ' in time_str:
                time_part = time_str.split()[-1]
            else:
                time_part = time_str
            
            # Parse HH:MM format
            if ':' in time_part:
                parts = time_part.split(':')
                hours = int(parts[0])
                minutes = int(parts[1]) if len(parts) > 1 else 0
                
                # Handle AM/PM
                if 'PM' in time_str.upper() and hours != 12:
                    hours += 12
                elif 'AM' in time_str.upper() and hours == 12:
                    hours = 0
                
                return hours * 60 + minutes
            
            return 0
        except:
            return 0
