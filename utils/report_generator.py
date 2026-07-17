"""
Report Generator Module
Generates Excel and PDF reports for sleep analysis
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import os


class ReportGenerator:
    """Generator for sleep analysis reports"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_excel_report(self, analysis_results: Dict[str, Any], filename: str = None) -> str:
        """Generate Excel report"""
        if filename is None:
            filename = f"sleep_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            self._write_summary_sheet(writer, analysis_results)
            
            # User claim comparison
            self._write_claim_comparison_sheet(writer, analysis_results)
            
            # Gap analysis
            self._write_gap_analysis_sheet(writer, analysis_results)
            
            # Initial awake analysis
            self._write_initial_awake_sheet(writer, analysis_results)
            
            # HR validation
            self._write_hr_validation_sheet(writer, analysis_results)
            
            # Nap detection
            self._write_nap_detection_sheet(writer, analysis_results)
            
            # Build comparison
            self._write_build_comparison_sheet(writer, analysis_results)
            
            # Root cause
            self._write_root_cause_sheet(writer, analysis_results)
        
        return filepath
    
    def _write_summary_sheet(self, writer, analysis_results: Dict):
        """Write summary sheet"""
        summary_data = []
        
        # User claim
        user_claim = analysis_results.get('user_claim', {})
        summary_data.append(['User Claim', ''])
        summary_data.append(['Sleep Start', user_claim.get('sleep_start', 'N/A')])
        summary_data.append(['Wake Time', user_claim.get('wake_time', 'N/A')])
        summary_data.append(['', ''])
        
        # JSON analysis
        json_analysis = analysis_results.get('sleep_analysis', {})
        summary_data.append(['JSON Analysis', ''])
        summary_data.append(['Sleep Start', json_analysis.get('sleep_start', 'N/A')])
        summary_data.append(['Sleep End', json_analysis.get('sleep_end', 'N/A')])
        summary_data.append(['Total Sleep Records', json_analysis.get('total_sleep_records', 'N/A')])
        summary_data.append(['', ''])
        
        # Root cause
        root_cause = analysis_results.get('root_cause', {})
        summary_data.append(['Root Cause', ''])
        summary_data.append(['Primary Cause', root_cause.get('primary_cause', 'N/A')])
        summary_data.append(['Verdict', root_cause.get('verdict', 'N/A')])
        summary_data.append(['Is Application Issue', root_cause.get('is_application_issue', 'N/A')])
        
        df = pd.DataFrame(summary_data, columns=['Field', 'Value'])
        df.to_excel(writer, sheet_name='Summary', index=False)
    
    def _write_claim_comparison_sheet(self, writer, analysis_results: Dict):
        """Write claim comparison sheet"""
        comparison = analysis_results.get('claim_comparison', {})
        
        data = [
            ['Metric', 'User Claim', 'JSON', 'JSON (Ignored Awake)', 'Match'],
            ['Sleep Start', comparison.get('claimed_sleep_start', 'N/A'), 
             comparison.get('json_sleep_start', 'N/A'),
             comparison.get('json_sleep_start_ignored', 'N/A'),
             comparison.get('start_match_ignored', 'N/A')],
            ['Wake Time', comparison.get('claimed_wake_time', 'N/A'),
             comparison.get('json_sleep_end', 'N/A'),
             'N/A',
             comparison.get('end_match', 'N/A')]
        ]
        
        df = pd.DataFrame(data[1:], columns=data[0])
        df.to_excel(writer, sheet_name='Claim Comparison', index=False)
    
    def _write_gap_analysis_sheet(self, writer, analysis_results: Dict):
        """Write gap analysis sheet"""
        gap_analysis = analysis_results.get('gap_analysis', {})
        gaps = gap_analysis.get('gaps', [])
        
        if gaps:
            data = [[
                'Gap Start', 'Gap End', 'Duration (mins)', 'Reason', 'Classification'
            ]]
            for gap in gaps:
                data.append([
                    gap.get('gap_start', 'N/A'),
                    gap.get('gap_end', 'N/A'),
                    gap.get('gap_duration_minutes', 'N/A'),
                    gap.get('reason', 'N/A'),
                    gap.get('classification', 'N/A')
                ])
            
            df = pd.DataFrame(data[1:], columns=data[0])
            df.to_excel(writer, sheet_name='Gap Analysis', index=False)
        else:
            df = pd.DataFrame([['No gaps detected']], columns=['Result'])
            df.to_excel(writer, sheet_name='Gap Analysis', index=False)
    
    def _write_initial_awake_sheet(self, writer, analysis_results: Dict):
        """Write initial awake sheet"""
        initial_awake = analysis_results.get('initial_awake', {})
        
        data = [
            ['Field', 'Value'],
            ['Has Initial Awake', initial_awake.get('has_initial_awake', 'N/A')],
            ['Duration (records)', initial_awake.get('duration_records', 'N/A')],
            ['Duration (minutes)', initial_awake.get('duration_minutes', 'N/A')],
            ['Awake Start', initial_awake.get('awake_start', 'N/A')],
            ['Awake End', initial_awake.get('awake_end', 'N/A')],
            ['Sleep Start (ignored awake)', initial_awake.get('sleep_start', 'N/A')],
            ['Matches User Claim', initial_awake.get('ignored_match', 'N/A')]
        ]
        
        df = pd.DataFrame(data[1:], columns=data[0])
        df.to_excel(writer, sheet_name='Initial Awake', index=False)
    
    def _write_hr_validation_sheet(self, writer, analysis_results: Dict):
        """Write HR validation sheet"""
        hr_validation = analysis_results.get('hr_validation', {})
        
        data = [
            ['Field', 'Value'],
            ['Claimed Sleep Time', hr_validation.get('claimed_sleep_time', 'N/A')],
            ['HR Average', hr_validation.get('hr_avg', 'N/A')],
            ['HR Trend', hr_validation.get('hr_trend', 'N/A')],
            ['HR Decreasing', hr_validation.get('hr_decreasing', 'N/A')],
            ['Supports Sleep', hr_validation.get('supports_sleep', 'N/A')],
            ['Classification', hr_validation.get('classification', 'N/A')]
        ]
        
        df = pd.DataFrame(data[1:], columns=data[0])
        df.to_excel(writer, sheet_name='HR Validation', index=False)
    
    def _write_nap_detection_sheet(self, writer, analysis_results: Dict):
        """Write nap detection sheet"""
        nap_analysis = analysis_results.get('nap_analysis', {})
        naps = nap_analysis.get('naps', [])
        
        if naps:
            data = [[
                'Time', 'Duration (mins)', 'Detected', 'JSON', 'Production', 'Test', 'Classification'
            ]]
            for nap in naps:
                data.append([
                    nap.get('time', 'N/A'),
                    nap.get('duration', 'N/A'),
                    nap.get('detected', 'N/A'),
                    nap.get('json', 'N/A'),
                    nap.get('production', 'N/A'),
                    nap.get('test', 'N/A'),
                    nap.get('classification', 'N/A')
                ])
            
            df = pd.DataFrame(data[1:], columns=data[0])
            df.to_excel(writer, sheet_name='Nap Detection', index=False)
        else:
            df = pd.DataFrame([['No naps detected']], columns=['Result'])
            df.to_excel(writer, sheet_name='Nap Detection', index=False)
    
    def _write_build_comparison_sheet(self, writer, analysis_results: Dict):
        """Write build comparison sheet"""
        comparison = analysis_results.get('build_comparison', {})
        table = comparison.get('comparison_table', [])
        
        if table:
            df = pd.DataFrame(table)
            df.to_excel(writer, sheet_name='Build Comparison', index=False)
        else:
            df = pd.DataFrame([['No build comparison data']], columns=['Result'])
            df.to_excel(writer, sheet_name='Build Comparison', index=False)
    
    def _write_root_cause_sheet(self, writer, analysis_results: Dict):
        """Write root cause sheet"""
        root_cause = analysis_results.get('root_cause', {})
        causes = root_cause.get('root_causes', [])
        
        if causes:
            data = [[
                'Cause', 'Severity', 'Description'
            ]]
            for cause in causes:
                data.append([
                    cause.get('cause', 'N/A'),
                    cause.get('severity', 'N/A'),
                    cause.get('description', 'N/A')
                ])
            
            df = pd.DataFrame(data[1:], columns=data[0])
            df.to_excel(writer, sheet_name='Root Cause', index=False)
        else:
            df = pd.DataFrame([['No root cause data']], columns=['Result'])
            df.to_excel(writer, sheet_name='Root Cause', index=False)
    
    def generate_text_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate text report for display"""
        report = []
        report.append("=" * 50)
        report.append("SLEEP INVESTIGATION REPORT")
        report.append("=" * 50)
        report.append("")
        
        # User Claim
        user_claim = analysis_results.get('user_claim', {})
        report.append("USER CLAIM")
        report.append("-" * 50)
        report.append(f"Sleep Start: {user_claim.get('sleep_start', 'N/A')}")
        report.append(f"Wake Time: {user_claim.get('wake_time', 'N/A')}")
        report.append("")
        
        # Analysis
        report.append("ANALYSIS")
        report.append("-" * 50)
        
        # Initial awake
        initial_awake = analysis_results.get('initial_awake', {})
        if initial_awake.get('has_initial_awake'):
            report.append(f"• Initial awake lasted {initial_awake.get('duration_minutes', 0)} minutes.")
            report.append(f"• Ignoring initial awake, sleep starts at {initial_awake.get('sleep_start', 'N/A')}.")
            if initial_awake.get('ignored_match'):
                report.append("• Matches user claim.")
        
        # HR validation
        hr_validation = analysis_results.get('hr_validation', {})
        if hr_validation.get('supports_sleep'):
            report.append("• Heart rate trend supports the user's claimed sleep onset.")
        elif hr_validation.get('classification'):
            report.append(f"• {hr_validation.get('classification', 'N/A')}.")
        
        # Gaps
        gap_analysis = analysis_results.get('gap_analysis', {})
        if gap_analysis.get('total_gaps', 0) > 0:
            report.append(f"• {gap_analysis.get('total_gaps', 0)} missing sleep records detected.")
            report.append(f"• Total missing time: {gap_analysis.get('total_missing_minutes', 0)} minutes.")
            report.append("• Indicates temporary ring data loss.")
        
        # Naps
        nap_analysis = analysis_results.get('nap_analysis', {})
        if nap_analysis.get('total_naps', 0) > 0:
            report.append(f"• {nap_analysis.get('total_naps', 0)} possible nap(s) detected.")
        else:
            report.append("• No nap events detected.")
        
        # Build comparison
        comparison = analysis_results.get('build_comparison', {})
        assessment = comparison.get('overall_assessment', {})
        if assessment.get('production_issues', 0) == 0 and assessment.get('test_issues', 0) == 0:
            report.append("• Production and Test Build match JSON.")
        
        report.append("")
        
        # Root Cause
        root_cause = analysis_results.get('root_cause', {})
        report.append("ROOT CAUSE")
        report.append("-" * 50)
        report.append(root_cause.get('verdict', 'N/A'))
        report.append("")
        
        # QA Remarks
        report.append("QA REMARKS")
        report.append("-" * 50)
        qa_engine = analysis_results.get('qa_remarks', '')
        report.append(qa_engine if qa_engine else "No remarks generated.")
        
        report.append("")
        report.append("=" * 50)
        
        return "\n".join(report)
    
    def generate_github_issue(self, analysis_results: Dict[str, Any]) -> str:
        """Generate GitHub issue format"""
        report = self.generate_text_report(analysis_results)
        
        github_issue = f"""
## Sleep Investigation Report

{report}

### Recommendation
{analysis_results.get('root_cause', {}).get('recommendation', 'N/A')}
"""
        return github_issue
