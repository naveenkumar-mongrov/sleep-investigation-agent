"""
Heart Rate Validator Module
Validates sleep claims using heart rate trends
"""

import pandas as pd
from typing import Dict, List, Any


class HRValidator:
    """Validator for heart rate data"""
    
    def __init__(self, hr_df: pd.DataFrame):
        self.hr_df = hr_df.copy()
        
    def validate_sleep_claim(self, claimed_sleep_time: str) -> Dict[str, Any]:
        """Validate sleep claim using heart rate data"""
        if self.hr_df.empty:
            return {'error': 'No heart rate data available'}
        
        # Parse claimed sleep time
        claimed_minutes = self._parse_time_to_minutes(claimed_sleep_time)
        
        # Get HR around claimed time
        hr_around_claim = self._get_hr_around_time(claimed_minutes, window_minutes=30)
        
        if hr_around_claim.empty:
            return {'error': 'No HR data around claimed time'}
        
        # Analyze HR trend
        hr_values = hr_around_claim['value'].tolist()
        
        analysis = {
            'claimed_sleep_time': claimed_sleep_time,
            'hr_values': hr_values[:10],  # First 10 values
            'hr_avg': sum(hr_values) / len(hr_values),
            'hr_trend': self._analyze_trend(hr_values),
            'hr_decreasing': self._is_decreasing(hr_values),
            'supports_sleep': self._supports_sleep_onset(hr_values),
            'classification': self._classify_validation(hr_values)
        }
        
        return analysis
    
    def _parse_time_to_minutes(self, time_str: str) -> int:
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
    
    def _get_hr_around_time(self, time_minutes: int, window_minutes: int = 30) -> pd.DataFrame:
        """Get HR data around a specific time"""
        if self.hr_df.empty or 'timestamp' not in self.hr_df.columns:
            return pd.DataFrame()
        
        # Parse all timestamps
        self.hr_df['time_minutes'] = self.hr_df['timestamp'].apply(self._parse_time_to_minutes)
        
        # Filter within window
        start = time_minutes - window_minutes
        end = time_minutes + window_minutes
        
        return self.hr_df[(self.hr_df['time_minutes'] >= start) & (self.hr_df['time_minutes'] <= end)]
    
    def _analyze_trend(self, hr_values: List[float]) -> str:
        """Analyze HR trend"""
        if len(hr_values) < 2:
            return "Insufficient data"
        
        first_half = hr_values[:len(hr_values)//2]
        second_half = hr_values[len(hr_values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg < first_avg - 5:
            return "Decreasing"
        elif second_avg > first_avg + 5:
            return "Increasing"
        else:
            return "Stable"
    
    def _is_decreasing(self, hr_values: List[float]) -> bool:
        """Check if HR is decreasing"""
        if len(hr_values) < 3:
            return False
        
        # Check if overall trend is decreasing
        decreases = 0
        for i in range(1, len(hr_values)):
            if hr_values[i] < hr_values[i-1]:
                decreases += 1
        
        return decreases >= len(hr_values) * 0.6
    
    def _supports_sleep_onset(self, hr_values: List[float]) -> bool:
        """Check if HR pattern supports sleep onset"""
        if len(hr_values) < 3:
            return False
        
        # Sleep onset typically shows gradual decrease
        # Check for decrease of at least 10 bpm over the period
        if max(hr_values) - min(hr_values) >= 10:
            return self._is_decreasing(hr_values)
        
        return False
    
    def _classify_validation(self, hr_values: List[float]) -> str:
        """Classify the validation result"""
        if self._supports_sleep_onset(hr_values):
            return "HR supports user claim"
        elif self._is_decreasing(hr_values):
            return "HR slightly decreasing - inconclusive"
        else:
            return "HR does not support sleep claim"
    
    def analyze_sleep_period(self, sleep_start: str, sleep_end: str) -> Dict[str, Any]:
        """Analyze HR throughout sleep period"""
        if self.hr_df.empty:
            return {'error': 'No heart rate data available'}
        
        start_minutes = self._parse_time_to_minutes(sleep_start)
        end_minutes = self._parse_time_to_minutes(sleep_end)
        
        # Get HR during sleep
        self.hr_df['time_minutes'] = self.hr_df['timestamp'].apply(self._parse_time_to_minutes)
        
        # Handle overnight (end < start)
        if end_minutes < start_minutes:
            sleep_hr = self.hr_df[(self.hr_df['time_minutes'] >= start_minutes) | (self.hr_df['time_minutes'] <= end_minutes)]
        else:
            sleep_hr = self.hr_df[(self.hr_df['time_minutes'] >= start_minutes) & (self.hr_df['time_minutes'] <= end_minutes)]
        
        if sleep_hr.empty:
            return {'error': 'No HR data during sleep period'}
        
        hr_values = sleep_hr['value'].tolist()
        
        return {
            'sleep_period_hr': hr_values,
            'hr_min': min(hr_values),
            'hr_max': max(hr_values),
            'hr_avg': sum(hr_values) / len(hr_values),
            'hr_samples': len(hr_values),
            'classification': 'Normal HR pattern during sleep' if len(hr_values) > 10 else 'Insufficient HR data'
        }
