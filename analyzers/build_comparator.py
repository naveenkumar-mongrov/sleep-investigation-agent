"""
Production/Test Comparison Module
Compares JSON data with Production and Test build data
"""

from typing import Dict, List, Any


class BuildComparator:
    """Comparator for Production vs Test vs JSON data"""
    
    def __init__(self, json_data: Dict, production_data: Dict, test_data: Dict):
        self.json_data = json_data
        self.production_data = production_data
        self.test_data = test_data
        
    def compare_all(self) -> Dict[str, Any]:
        """Compare all sleep metrics across JSON, Production, and Test"""
        comparison = {
            'sleep_start': self._compare_field('sleep_start'),
            'sleep_end': self._compare_field('sleep_end'),
            'deep_sleep': self._compare_field('deep'),
            'light_sleep': self._compare_field('light'),
            'rem_sleep': self._compare_field('rem'),
            'awake': self._compare_field('awake'),
            'total_sleep': self._compare_field('total_sleep')
        }
        
        # Generate overall assessment
        comparison['overall_assessment'] = self._generate_assessment(comparison)
        
        return comparison
    
    def _compare_field(self, field: str) -> Dict[str, Any]:
        """Compare a single field across all sources"""
        json_value = self.json_data.get(field, 'N/A')
        production_value = self.production_data.get(field, 'N/A')
        test_value = self.test_data.get(field, 'N/A')
        
        # Check matches
        json_matches_production = self._values_match(json_value, production_value)
        json_matches_test = self._values_match(json_value, test_value)
        production_matches_test = self._values_match(production_value, test_value)
        
        return {
            'json': json_value,
            'production': production_value,
            'test': test_value,
            'json_matches_production': json_matches_production,
            'json_matches_test': json_matches_test,
            'production_matches_test': production_matches_test,
            'status': self._determine_status(json_matches_production, json_matches_test, production_matches_test)
        }
    
    def _values_match(self, val1: Any, val2: Any, tolerance: float = 0.1) -> bool:
        """Check if two values match (with tolerance for numeric values)"""
        if val1 == val2:
            return True
        
        # Try numeric comparison with tolerance
        try:
            num1 = float(val1)
            num2 = float(val2)
            if num1 == 0:
                return num2 == 0
            return abs(num1 - num2) / num1 <= tolerance
        except (ValueError, TypeError):
            return False
    
    def _determine_status(self, json_prod: bool, json_test: bool, prod_test: bool) -> str:
        """Determine overall status for a field"""
        if json_prod and json_test and prod_test:
            return 'Pass - All Match'
        elif json_prod and not json_test:
            return 'Test Build Issue'
        elif not json_prod and json_test:
            return 'Production Issue'
        elif not json_prod and not json_test and prod_test:
            return 'JSON Issue'
        elif not json_prod and not json_test and not prod_test:
            return 'All Mismatch'
        else:
            return 'Partial Match'
    
    def _generate_assessment(self, comparison: Dict) -> Dict[str, Any]:
        """Generate overall assessment"""
        fields = comparison.keys()
        
        pass_count = sum(1 for f in fields if 'Pass' in comparison[f]['status'])
        prod_issue_count = sum(1 for f in fields if 'Production Issue' in comparison[f]['status'])
        test_issue_count = sum(1 for f in fields if 'Test Build Issue' in comparison[f]['status'])
        json_issue_count = sum(1 for f in fields if 'JSON Issue' in comparison[f]['status'])
        
        return {
            'total_fields': len(fields),
            'pass_count': pass_count,
            'production_issues': prod_issue_count,
            'test_issues': test_issue_count,
            'json_issues': json_issue_count,
            'overall_status': self._overall_status(pass_count, len(fields))
        }
    
    def _overall_status(self, pass_count: int, total: int) -> str:
        """Determine overall status"""
        if pass_count == total:
            return 'All Systems Pass'
        elif pass_count >= total * 0.7:
            return 'Mostly Pass'
        elif pass_count >= total * 0.5:
            return 'Partial Pass'
        else:
            return 'Multiple Issues Detected'
    
    def generate_comparison_table(self) -> List[Dict[str, str]]:
        """Generate comparison table for report"""
        comparison = self.compare_all()
        
        table = []
        for field, data in comparison.items():
            if field == 'overall_assessment':
                continue
            
            table.append({
                'Feature': field.replace('_', ' ').title(),
                'JSON': str(data['json']),
                'Production': str(data['production']),
                'Test': str(data['test']),
                'Result': data['status']
            })
        
        return table
    
    def identify_discrepancies(self) -> List[Dict[str, Any]]:
        """Identify specific discrepancies between builds"""
        comparison = self.compare_all()
        discrepancies = []
        
        for field, data in comparison.items():
            if field == 'overall_assessment':
                continue
            
            if not data['json_matches_production'] or not data['json_matches_test']:
                discrepancies.append({
                    'field': field,
                    'json_value': data['json'],
                    'production_value': data['production'],
                    'test_value': data['test'],
                    'issue_type': data['status']
                })
        
        return discrepancies
