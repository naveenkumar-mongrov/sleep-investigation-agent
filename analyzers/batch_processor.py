"""
Batch Processor Module
Processes multiple JSON files for batch analysis of 100+ users
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

from analyzers import (
    JSONParser, SleepAnalyzer, GapDetector, InitialAwakeDetector,
    HRValidator, NapDetector, BuildComparator, RootCauseEngine
)
from utils import ReportGenerator, DataIntegrator
from ai import AIInvestigator


class BatchProcessor:
    """Processor for batch analysis of multiple user JSON files"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        google_sheets_api_key: Optional[str] = None,
        github_token: Optional[str] = None
    ):
        self.api_key = api_key
        self.ai_investigator = AIInvestigator(api_key)
        self.data_integrator = DataIntegrator(google_sheets_api_key, github_token)
        self.results = []
        
    def process_single_user(
        self,
        json_path: str,
        user_claim: Dict[str, str],
        production_data: Dict[str, str],
        test_data: Dict[str, str],
        user_id: str = None
    ) -> Dict[str, Any]:
        """Process a single user's data"""
        try:
            # Parse JSON
            parser = JSONParser(json_path)
            parsed_data = parser.parse_all()
            
            # Skip if no sleep data
            if parsed_data['sleep_records'].empty:
                return {
                    'user_id': user_id or os.path.basename(json_path),
                    'status': 'error',
                    'error': 'No sleep data found in JSON'
                }
            
            # Sleep analysis
            sleep_analyzer = SleepAnalyzer(parsed_data['sleep_records'])
            sleep_analysis = sleep_analyzer.analyze_sleep_periods()
            
            # Claim comparison
            claim_comparison = sleep_analyzer.compare_with_claim(
                user_claim.get('sleep_start', ''),
                user_claim.get('wake_time', '')
            )
            
            # Gap detection
            gap_detector = GapDetector(parsed_data['sleep_records'])
            gap_analysis = gap_detector.get_gap_summary()
            
            # Initial awake detection
            awake_detector = InitialAwakeDetector(parsed_data['sleep_records'])
            initial_awake = awake_detector.detect_initial_awake()
            initial_awake_comparison = awake_detector.compare_with_claim(user_claim.get('sleep_start', ''))
            
            # HR validation
            hr_validator = HRValidator(parsed_data['heart_rate'])
            hr_validation = hr_validator.validate_sleep_claim(user_claim.get('sleep_start', ''))
            
            # Nap detection
            nap_detector = NapDetector(
                parsed_data['sleep_records'],
                parsed_data['heart_rate'],
                parsed_data['activity']
            )
            naps = nap_detector.detect_naps()
            nap_analysis = nap_detector.check_nap_in_builds(production_data, test_data)
            
            # Build comparison
            build_comparator = BuildComparator(sleep_analysis, production_data, test_data)
            build_comparison = build_comparator.compare_all()
            
            # Root cause analysis
            all_results = {
                'user_claim': user_claim,
                'sleep_analysis': sleep_analysis,
                'claim_comparison': claim_comparison,
                'gap_analysis': gap_analysis,
                'initial_awake': initial_awake_comparison,
                'hr_validation': hr_validation,
                'nap_analysis': nap_analysis,
                'build_comparison': build_comparison
            }
            
            root_cause_engine = RootCauseEngine(all_results)
            root_cause = root_cause_engine.determine_root_cause()
            qa_remarks = root_cause_engine.generate_qa_remarks()
            recommendation = root_cause_engine.get_recommendation()
            
            # AI investigation (real-time)
            ai_summary = self.ai_investigator.generate_investigation_summary(all_results)
            ai_qa_remarks = self.ai_investigator.generate_qa_remarks(all_results)
            
            return {
                'user_id': user_id or os.path.basename(json_path),
                'status': 'success',
                'user_claim': user_claim,
                'sleep_analysis': sleep_analysis,
                'claim_comparison': claim_comparison,
                'gap_analysis': gap_analysis,
                'initial_awake': initial_awake_comparison,
                'hr_validation': hr_validation,
                'nap_analysis': nap_analysis,
                'build_comparison': build_comparison,
                'root_cause': root_cause,
                'qa_remarks': qa_remarks,
                'recommendation': recommendation,
                'ai_summary': ai_summary,
                'ai_qa_remarks': ai_qa_remarks,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'user_id': user_id or os.path.basename(json_path),
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def process_batch(
        self,
        json_files: List[str],
        user_claims: List[Dict[str, str]],
        production_data_list: List[Dict[str, str]],
        test_data_list: List[Dict[str, str]],
        user_ids: List[str] = None,
        max_workers: int = 4
    ) -> Dict[str, Any]:
        """Process multiple users in parallel"""
        self.results = []
        
        total_users = len(json_files)
        processed = 0
        errors = 0
        
        print(f"Starting batch processing for {total_users} users...")
        
        # Process in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for i, json_file in enumerate(json_files):
                user_id = user_ids[i] if user_ids and i < len(user_ids) else None
                user_claim = user_claims[i] if i < len(user_claims) else {}
                prod_data = production_data_list[i] if i < len(production_data_list) else {}
                test_data = test_data_list[i] if i < len(test_data_list) else {}
                
                future = executor.submit(
                    self.process_single_user,
                    json_file,
                    user_claim,
                    prod_data,
                    test_data,
                    user_id
                )
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)
                processed += 1
                
                if result['status'] == 'error':
                    errors += 1
                
                print(f"Progress: {processed}/{total_users} users processed")
        
        # Generate summary
        summary = self.generate_batch_summary()
        
        return {
            'total_users': total_users,
            'processed': processed,
            'errors': errors,
            'success_rate': (processed - errors) / total_users * 100 if total_users > 0 else 0,
            'results': self.results,
            'summary': summary
        }
    
    def process_batch_from_directory(
        self,
        json_directory: str,
        claims_file: str = None,
        max_workers: int = 4
    ) -> Dict[str, Any]:
        """Process all JSON files from a directory"""
        # Get all JSON files
        json_files = [
            os.path.join(json_directory, f)
            for f in os.listdir(json_directory)
            if f.endswith('.json')
        ]
        
        if not json_files:
            return {
                'total_users': 0,
                'processed': 0,
                'errors': 0,
                'results': [],
                'summary': {},
                'error': 'No JSON files found in directory'
            }
        
        # Load claims if provided
        user_claims = []
        production_data_list = []
        test_data_list = []
        user_ids = []
        
        if claims_file and os.path.exists(claims_file):
            with open(claims_file, 'r') as f:
                claims_data = json.load(f)
            
            # Map claims to files
            claims_map = {claim.get('filename', ''): claim for claim in claims_data}
            
            for json_file in json_files:
                filename = os.path.basename(json_file)
                claim = claims_map.get(filename, {})
                
                user_ids.append(claim.get('user_id', filename))
                user_claims.append({
                    'sleep_start': claim.get('sleep_start', ''),
                    'wake_time': claim.get('wake_time', ''),
                    'awake_during': claim.get('awake_during', ''),
                    'nap': claim.get('nap', ''),
                    'remarks': claim.get('remarks', '')
                })
                production_data_list.append(claim.get('production_data', {}))
                test_data_list.append(claim.get('test_data', {}))
        else:
            # Use empty claims
            for json_file in json_files:
                user_ids.append(os.path.basename(json_file))
                user_claims.append({})
                production_data_list.append({})
                test_data_list.append({})
        
        return self.process_batch(
            json_files,
            user_claims,
            production_data_list,
            test_data_list,
            user_ids,
            max_workers
        )
    
    def generate_batch_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for batch processing"""
        if not self.results:
            return {}
        
        successful_results = [r for r in self.results if r['status'] == 'success']
        
        # Root cause distribution
        root_cause_counts = {}
        for result in successful_results:
            cause = result.get('root_cause', {}).get('primary_cause', 'Unknown')
            root_cause_counts[cause] = root_cause_counts.get(cause, 0) + 1
        
        # Application issues count
        app_issues = sum(
            1 for r in successful_results
            if r.get('root_cause', {}).get('is_application_issue', False)
        )
        
        # Initial awake issues
        initial_awake_issues = sum(
            1 for r in successful_results
            if r.get('initial_awake', {}).get('has_initial_awake', False)
        )
        
        # Gap issues
        gap_issues = sum(
            1 for r in successful_results
            if r.get('gap_analysis', {}).get('total_gaps', 0) > 0
        )
        
        # HR validation
        hr_supported = sum(
            1 for r in successful_results
            if r.get('hr_validation', {}).get('supports_sleep', False)
        )
        
        return {
            'total_successful': len(successful_results),
            'total_errors': len(self.results) - len(successful_results),
            'root_cause_distribution': root_cause_counts,
            'application_issues': app_issues,
            'initial_awake_issues': initial_awake_issues,
            'gap_issues': gap_issues,
            'hr_supported_claims': hr_supported,
            'most_common_issue': max(root_cause_counts.items(), key=lambda x: x[1])[0] if root_cause_counts else 'None'
        }
    
    def export_batch_results(self, output_dir: str = "reports") -> str:
        """Export batch results to Excel"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"batch_analysis_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        # Create summary DataFrame
        summary_data = []
        for result in self.results:
            if result['status'] == 'success':
                summary_data.append({
                    'User ID': result['user_id'],
                    'Status': result['status'],
                    'Sleep Start': result.get('claim_comparison', {}).get('json_sleep_start', 'N/A'),
                    'Initial Awake': result.get('initial_awake', {}).get('has_initial_awake', False),
                    'Gaps': result.get('gap_analysis', {}).get('total_gaps', 0),
                    'HR Supports': result.get('hr_validation', {}).get('supports_sleep', False),
                    'Root Cause': result.get('root_cause', {}).get('primary_cause', 'N/A'),
                    'App Issue': result.get('root_cause', {}).get('is_application_issue', False),
                    'AI Summary': result.get('ai_summary', 'N/A')[:100] + '...' if len(result.get('ai_summary', '')) > 100 else result.get('ai_summary', 'N/A'),
                    'QA Remarks': result.get('qa_remarks', 'N/A')[:100] + '...' if len(result.get('qa_remarks', '')) > 100 else result.get('qa_remarks', 'N/A')
                })
            else:
                summary_data.append({
                    'User ID': result['user_id'],
                    'Status': result['status'],
                    'Error': result.get('error', 'N/A')
                })
        
        summary_df = pd.DataFrame(summary_data)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Add detailed sheets for each user
            for result in self.results:
                if result['status'] == 'success':
                    user_id = result['user_id'][:31]  # Excel sheet name limit
                    user_data = pd.DataFrame([result])
                    user_data.to_excel(writer, sheet_name=user_id, index=False)
        
        return filepath
    
    def generate_claims_template(self, output_path: str = "claims_template.json") -> str:
        """Generate a template for user claims"""
        template = [
            {
                "filename": "user1.json",
                "user_id": "user001",
                "sleep_start": "11:20 PM",
                "wake_time": "7:10 AM",
                "awake_during": "2 times",
                "nap": "",
                "remarks": "",
                "production_data": {
                    "sleep_start": "11:18 PM",
                    "sleep_end": "7:08 AM",
                    "deep": "90",
                    "light": "240",
                    "rem": "105",
                    "awake": "15"
                },
                "test_data": {
                    "sleep_start": "11:18 PM",
                    "sleep_end": "7:08 AM",
                    "deep": "90",
                    "light": "240",
                    "rem": "105",
                    "awake": "15"
                }
            }
        ]
        
        with open(output_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        return output_path
    
    def process_from_external_sources(
        self,
        google_sheets_id: Optional[str] = None,
        github_owner: Optional[str] = None,
        github_repo: Optional[str] = None,
        github_path: str = "",
        sheet_name: str = "Sheet1",
        column_mapping: Optional[Dict[str, str]] = None,
        max_workers: int = 4
    ) -> Dict[str, Any]:
        """Fetch data from external sources and process batch"""
        
        # Fetch data from external sources
        external_data = self.data_integrator.fetch_batch_data(
            google_sheets_id=google_sheets_id,
            github_owner=github_owner,
            github_repo=github_repo,
            github_path=github_path,
            sheet_name=sheet_name,
            column_mapping=column_mapping
        )
        
        if external_data.get('errors'):
            print(f"Errors fetching external data: {external_data['errors']}")
        
        # Process the fetched data
        json_files = external_data.get('json_files', [])
        claims = external_data.get('claims', [])
        
        if not json_files:
            return {
                'total_users': 0,
                'processed': 0,
                'errors': 0,
                'results': [],
                'summary': {},
                'external_data': external_data,
                'error': 'No JSON files found from external sources'
            }
        
        # Map claims to JSON files
        user_claims = []
        production_data_list = []
        test_data_list = []
        user_ids = []
        
        claims_map = {claim.get('filename', ''): claim for claim in claims}
        
        for json_file in json_files:
            filename = os.path.basename(json_file)
            claim = claims_map.get(filename, {})
            
            user_ids.append(claim.get('user_id', filename))
            user_claims.append({
                'sleep_start': claim.get('sleep_start', ''),
                'wake_time': claim.get('wake_time', ''),
                'awake_during': claim.get('awake_during', ''),
                'nap': claim.get('nap', ''),
                'remarks': claim.get('remarks', '')
            })
            production_data_list.append(claim.get('production_data', {}))
            test_data_list.append(claim.get('test_data', {}))
        
        # Process batch
        batch_results = self.process_batch(
            json_files,
            user_claims,
            production_data_list,
            test_data_list,
            user_ids,
            max_workers
        )
        
        # Add external data info to results
        batch_results['external_data'] = external_data
        batch_results['data_source'] = 'external'
        
        return batch_results
