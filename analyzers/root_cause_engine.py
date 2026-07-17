"""
Root Cause Engine Module
Classifies the root cause of sleep discrepancies
"""

from typing import Dict, List, Any


class RootCauseEngine:
    """Engine for determining root cause of sleep issues"""
    
    def __init__(self, analysis_results: Dict[str, Any]):
        self.analysis_results = analysis_results
        
    def determine_root_cause(self) -> Dict[str, Any]:
        """Determine the root cause based on all analysis results"""
        root_causes = []
        
        # Check for missing records
        if self._has_missing_records():
            root_causes.append({
                'cause': 'Ring missed sleep records',
                'severity': 'Medium',
                'description': 'Temporary ring data capture loss detected'
            })
        
        # Check initial awake issue
        if self._has_initial_awake_issue():
            root_causes.append({
                'cause': 'Initial awake incorrectly considered',
                'severity': 'High',
                'description': 'Initial awake period extends sleep start time'
            })
        
        # Check nap detection
        if self._has_missing_nap():
            root_causes.append({
                'cause': 'Possible nap not detected',
                'severity': 'Low',
                'description': 'Nap event may not be generated in JSON'
            })
        
        # Check JSON vs Production
        if self._has_production_issue():
            root_causes.append({
                'cause': 'Production build issue',
                'severity': 'High',
                'description': 'Production build does not match JSON data'
            })
        
        # Check JSON vs Test
        if self._has_test_issue():
            root_causes.append({
                'cause': 'Test build issue',
                'severity': 'High',
                'description': 'Test build does not match JSON data'
            })
        
        # Check HR validation
        hr_validation = self.analysis_results.get('hr_validation', {})
        if hr_validation.get('supports_sleep'):
            root_causes.append({
                'cause': 'HR supports user claim',
                'severity': 'Info',
                'description': 'Heart rate trend supports user-reported sleep time'
            })
        elif hr_validation.get('classification') == 'HR does not support sleep claim':
            root_causes.append({
                'cause': 'HR does not support user claim',
                'severity': 'Medium',
                'description': 'Heart rate does not indicate sleep at claimed time'
            })
        
        # Check if no issue found
        if not root_causes:
            root_causes.append({
                'cause': 'No issue found',
                'severity': 'Info',
                'description': 'All checks passed - no discrepancies detected'
            })
        
        # Generate final verdict
        verdict = self._generate_verdict(root_causes)
        
        return {
            'root_causes': root_causes,
            'primary_cause': root_causes[0]['cause'] if root_causes else 'Unknown',
            'verdict': verdict,
            'is_application_issue': self._is_application_issue(root_causes)
        }
    
    def _has_missing_records(self) -> bool:
        """Check if there are missing sleep records"""
        gap_analysis = self.analysis_results.get('gap_analysis', {})
        return gap_analysis.get('total_gaps', 0) > 0
    
    def _has_initial_awake_issue(self) -> bool:
        """Check if initial awake is causing issues"""
        initial_awake = self.analysis_results.get('initial_awake', {})
        return initial_awake.get('has_initial_awake', False) and \
               initial_awake.get('ignored_match', False)
    
    def _has_missing_nap(self) -> bool:
        """Check if there are missing naps"""
        nap_analysis = self.analysis_results.get('nap_analysis', {})
        return nap_analysis.get('missing_in_production', 0) > 0 or \
               nap_analysis.get('missing_in_test', 0) > 0
    
    def _has_production_issue(self) -> bool:
        """Check if there are production build issues"""
        comparison = self.analysis_results.get('build_comparison', {})
        assessment = comparison.get('overall_assessment', {})
        return assessment.get('production_issues', 0) > 0
    
    def _has_test_issue(self) -> bool:
        """Check if there are test build issues"""
        comparison = self.analysis_results.get('build_comparison', {})
        assessment = comparison.get('overall_assessment', {})
        return assessment.get('test_issues', 0) > 0
    
    def _generate_verdict(self, root_causes: List[Dict]) -> str:
        """Generate final verdict summary"""
        if not root_causes:
            return "No issues detected - data is consistent"
        
        high_severity = [c for c in root_causes if c['severity'] == 'High']
        medium_severity = [c for c in root_causes if c['severity'] == 'Medium']
        
        if high_severity:
            causes = ", ".join([c['cause'] for c in high_severity])
            return f"High priority issue: {causes}"
        elif medium_severity:
            causes = ", ".join([c['cause'] for c in medium_severity])
            return f"Medium priority issue: {causes}"
        else:
            return "Minor issues detected - no critical problems"
    
    def _is_application_issue(self, root_causes: List[Dict]) -> bool:
        """Determine if this is an application issue"""
        app_issue_causes = [
            'Production build issue',
            'Test build issue'
        ]
        
        for cause in root_causes:
            if cause['cause'] in app_issue_causes:
                return True
        
        return False
    
    def generate_qa_remarks(self) -> str:
        """Generate QA remarks in standard format"""
        root_cause = self.determine_root_cause()
        causes = root_cause['root_causes']
        
        remarks = []
        
        for cause in causes:
            if cause['cause'] == 'Ring missed sleep records':
                remarks.append("Ring didn't capture sleep data. Not an application issue.")
            elif cause['cause'] == 'Initial awake incorrectly considered':
                remarks.append("Ignoring the initial awake period aligns with the user's reported sleep time.")
            elif cause['cause'] == 'Possible nap not detected':
                remarks.append("Possible nap event not generated in JSON.")
            elif cause['cause'] == 'Production build issue':
                remarks.append("Production build does not match JSON data. Application issue detected.")
            elif cause['cause'] == 'Test build issue':
                remarks.append("Test build does not match JSON data. Application issue detected.")
            elif cause['cause'] == 'HR supports user claim':
                remarks.append("Heart rate trend supports the user's claimed sleep onset.")
            elif cause['cause'] == 'HR does not support user claim':
                remarks.append("Heart rate does not support the user's claimed sleep time.")
            elif cause['cause'] == 'No issue found':
                remarks.append("Production and Test Build match JSON. No application issue detected.")
        
        return "\n".join(remarks)
    
    def get_recommendation(self) -> str:
        """Get recommendation for next steps"""
        root_cause = self.determine_root_cause()
        
        if root_cause['is_application_issue']:
            return "Application issue detected - assign to development team for investigation."
        elif root_cause['primary_cause'] == 'Ring missed sleep records':
            return "Ring data capture issue - not an application problem. May be firmware/device related."
        elif root_cause['primary_cause'] == 'Initial awake incorrectly considered':
            return "Algorithm tuning needed for initial awake detection."
        elif root_cause['primary_cause'] == 'Possible nap not detected':
            return "Nap detection limitation - firmware may not capture short sleep periods."
        else:
            return "No action required - data is consistent."
