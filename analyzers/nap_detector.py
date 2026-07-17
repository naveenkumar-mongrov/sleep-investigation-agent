"""
Nap Detector Module
Detects potential nap events from HR, movement, and sleep stages
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any


class NapDetector:
    """Detector for nap events"""
    
    def __init__(self, sleep_df: pd.DataFrame, hr_df: pd.DataFrame, activity_df: pd.DataFrame):
        self.sleep_df = sleep_df.copy()
        self.hr_df = hr_df.copy()
        self.activity_df = activity_df.copy()
        self.detected_naps = []
        
    def detect_naps(self, min_duration_minutes: int = 20) -> List[Dict[str, Any]]:
        """Detect potential nap events"""
        self.detected_naps = []
        
        # Look for sleep periods outside main sleep window
        # This is a simplified approach - in production, you'd need to know the main sleep window
        
        if self.sleep_df.empty:
            return []
        
        # Find all sleep periods
        sleep_periods = self._identify_sleep_periods()
        
        # Filter for potential naps (shorter duration, daytime)
        for period in sleep_periods:
            duration_minutes = period['duration_minutes']
            hour = self._get_hour(period['start_time'])
            
            # Nap criteria: 20-120 minutes, typically daytime (8 AM - 8 PM)
            if min_duration_minutes <= duration_minutes <= 120 and 8 <= hour <= 20:
                nap_info = self._analyze_potential_nap(period)
                nap_info['classification'] = 'Possible Nap'
                self.detected_naps.append(nap_info)
        
        return self.detected_naps
    
    def _identify_sleep_periods(self) -> List[Dict[str, Any]]:
        """Identify distinct sleep periods"""
        if self.sleep_df.empty or 'timestamp' not in self.sleep_df.columns:
            return []
        
        sleep_only = self.sleep_df[self.sleep_df['is_sleep']].copy()
        sleep_only = sleep_only.sort_values('timestamp')
        
        if sleep_only.empty:
            return []
        
        periods = []
        current_period = None
        
        for idx, row in sleep_only.iterrows():
            timestamp = row['timestamp']
            
            if current_period is None:
                current_period = {'start_time': timestamp, 'end_time': timestamp, 'records': 1}
            else:
                # Check if this is continuous (within 10 minutes)
                if self._time_diff_minutes(current_period['end_time'], timestamp) <= 10:
                    current_period['end_time'] = timestamp
                    current_period['records'] += 1
                else:
                    # End current period
                    current_period['duration_minutes'] = self._time_diff_minutes(
                        current_period['start_time'], 
                        current_period['end_time']
                    )
                    periods.append(current_period)
                    current_period = {'start_time': timestamp, 'end_time': timestamp, 'records': 1}
        
        # Don't forget the last period
        if current_period:
            current_period['duration_minutes'] = self._time_diff_minutes(
                current_period['start_time'], 
                current_period['end_time']
            )
            periods.append(current_period)
        
        return periods
    
    def _analyze_potential_nap(self, period: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a potential nap period"""
        start_time = period['start_time']
        end_time = period['end_time']
        
        # Check HR during this period
        hr_analysis = self._analyze_hr_during_period(start_time, end_time)
        
        # Check movement/activity
        activity_analysis = self._analyze_activity_during_period(start_time, end_time)
        
        return {
            'start_time': start_time,
            'end_time': end_time,
            'duration_minutes': period['duration_minutes'],
            'hr_low': hr_analysis.get('hr_low', 'Unknown'),
            'hr_avg': hr_analysis.get('hr_avg', 'Unknown'),
            'movement_low': activity_analysis.get('movement_low', False),
            'in_json': True,  # Found in JSON sleep records
            'hr_supports_sleep': hr_analysis.get('supports_sleep', False)
        }
    
    def _analyze_hr_during_period(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """Analyze HR during a time period"""
        if self.hr_df.empty or 'timestamp' not in self.hr_df.columns:
            return {'hr_low': 'Unknown', 'hr_avg': 'Unknown', 'supports_sleep': False}
        
        start_min = self._parse_time_to_minutes(start_time)
        end_min = self._parse_time_to_minutes(end_time)
        
        self.hr_df['time_minutes'] = self.hr_df['timestamp'].apply(self._parse_time_to_minutes)
        
        # Handle overnight
        if end_min < start_min:
            period_hr = self.hr_df[(self.hr_df['time_minutes'] >= start_min) | (self.hr_df['time_minutes'] <= end_min)]
        else:
            period_hr = self.hr_df[(self.hr_df['time_minutes'] >= start_min) & (self.hr_df['time_minutes'] <= end_min)]
        
        if period_hr.empty:
            return {'hr_low': 'Unknown', 'hr_avg': 'Unknown', 'supports_sleep': False}
        
        hr_values = period_hr['value'].tolist()
        
        return {
            'hr_low': min(hr_values),
            'hr_avg': sum(hr_values) / len(hr_values),
            'supports_sleep': min(hr_values) < 70  # Low HR suggests sleep
        }
    
    def _analyze_activity_during_period(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """Analyze activity during a time period"""
        if self.activity_df.empty or 'timestamp' not in self.activity_df.columns:
            return {'movement_low': True, 'steps': 0}  # Assume low if no data
        
        start_min = self._parse_time_to_minutes(start_time)
        end_min = self._parse_time_to_minutes(end_time)
        
        self.activity_df['time_minutes'] = self.activity_df['timestamp'].apply(self._parse_time_to_minutes)
        
        if end_min < start_min:
            period_activity = self.activity_df[(self.activity_df['time_minutes'] >= start_min) | (self.activity_df['time_minutes'] <= end_min)]
        else:
            period_activity = self.activity_df[(self.activity_df['time_minutes'] >= start_min) & (self.activity_df['time_minutes'] <= end_min)]
        
        if period_activity.empty:
            return {'movement_low': True, 'steps': 0}
        
        total_steps = period_activity['steps'].sum() if 'steps' in period_activity.columns else 0
        
        return {
            'movement_low': total_steps < 50,  # Low movement threshold
            'steps': total_steps
        }
    
    def _time_diff_minutes(self, time1: str, time2: str) -> int:
        """Calculate time difference in minutes"""
        try:
            min1 = self._parse_time_to_minutes(time1)
            min2 = self._parse_time_to_minutes(time2)
            return abs(min2 - min1)
        except:
            return 0
    
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
    
    def _get_hour(self, time_str: str) -> int:
        """Get hour from time string"""
        try:
            minutes = self._parse_time_to_minutes(time_str)
            return (minutes // 60) % 24
        except:
            return 12
    
    def check_nap_in_builds(self, production_data: Dict, test_data: Dict) -> Dict[str, Any]:
        """Check if detected naps appear in production/test builds"""
        results = []
        
        for nap in self.detected_naps:
            nap_result = {
                'time': f"{nap['start_time']} - {nap['end_time']}",
                'duration': nap['duration_minutes'],
                'detected': 'Yes',
                'json': 'Yes',
                'production': self._check_nap_in_build(nap, production_data),
                'test': self._check_nap_in_build(nap, test_data),
                'classification': 'Possible Nap' if nap['hr_supports_sleep'] else 'Uncertain'
            }
            results.append(nap_result)
        
        return {
            'naps': results,
            'total_naps': len(results),
            'missing_in_production': sum(1 for r in results if r['production'] == 'No'),
            'missing_in_test': sum(1 for r in results if r['test'] == 'No')
        }
    
    def _check_nap_in_build(self, nap: Dict, build_data: Dict) -> str:
        """Check if nap appears in build data"""
        if not build_data:
            return 'No'
        
        # Simple check - in production, you'd compare timestamps
        # For now, assume if build has nap data, it would be indicated
        if build_data.get('has_nap'):
            return 'Yes'
        return 'No'
