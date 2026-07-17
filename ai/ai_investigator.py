"""
AI Investigation Module
Uses OpenAI API to generate human-readable investigation summaries
"""

import os
from typing import Dict, List, Any, Optional


class AIInvestigator:
    """AI-powered investigation summary generator"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI package not installed. AI features disabled.")
        
    def generate_investigation_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Generate AI-powered investigation summary"""
        if not self.client:
            return self._generate_fallback_summary(analysis_results)
        
        prompt = self._build_prompt(analysis_results)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sleep data analysis expert. Generate clear, concise investigation summaries based on sleep analysis data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_fallback_summary(analysis_results)
    
    def _build_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """Build prompt for AI"""
        user_claim = analysis_results.get('user_claim', {})
        sleep_analysis = analysis_results.get('sleep_analysis', {})
        initial_awake = analysis_results.get('initial_awake', {})
        hr_validation = analysis_results.get('hr_validation', {})
        gap_analysis = analysis_results.get('gap_analysis', {})
        nap_analysis = analysis_results.get('nap_analysis', {})
        root_cause = analysis_results.get('root_cause', {})
        
        prompt = f"""
Generate a concise sleep investigation summary based on the following data:

User Claim:
- Sleep Start: {user_claim.get('sleep_start', 'N/A')}
- Wake Time: {user_claim.get('wake_time', 'N/A')}

Sleep Analysis:
- Sleep Start: {sleep_analysis.get('sleep_start', 'N/A')}
- Sleep End: {sleep_analysis.get('sleep_end', 'N/A')}
- Total Sleep Records: {sleep_analysis.get('total_sleep_records', 'N/A')}

Initial Awake:
- Has Initial Awake: {initial_awake.get('has_initial_awake', False)}
- Duration: {initial_awake.get('duration_minutes', 0)} minutes
- Sleep Start (ignored awake): {initial_awake.get('sleep_start', 'N/A')}
- Matches User Claim: {initial_awake.get('ignored_match', False)}

Heart Rate Validation:
- Classification: {hr_validation.get('classification', 'N/A')}
- Supports Sleep: {hr_validation.get('supports_sleep', False)}

Gap Analysis:
- Total Gaps: {gap_analysis.get('total_gaps', 0)}
- Total Missing Minutes: {gap_analysis.get('total_missing_minutes', 0)}

Nap Detection:
- Total Naps: {nap_analysis.get('total_naps', 0)}

Root Cause:
- Primary Cause: {root_cause.get('primary_cause', 'N/A')}
- Is Application Issue: {root_cause.get('is_application_issue', False)}

Generate a 2-3 sentence summary explaining the findings and root cause.
"""
        return prompt
    
    def _generate_fallback_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Generate summary without AI"""
        user_claim = analysis_results.get('user_claim', {})
        initial_awake = analysis_results.get('initial_awake', {})
        hr_validation = analysis_results.get('hr_validation', {})
        gap_analysis = analysis_results.get('gap_analysis', {})
        root_cause = analysis_results.get('root_cause', {})
        
        summary_parts = []
        
        # Initial awake
        if initial_awake.get('has_initial_awake'):
            if initial_awake.get('ignored_match'):
                summary_parts.append(
                    f"Ignoring the initial awake period ({initial_awake.get('duration_minutes', 0)} minutes), "
                    f"sleep start matches the user's claimed time of {user_claim.get('sleep_start', 'N/A')}."
                )
        
        # HR validation
        if hr_validation.get('supports_sleep'):
            summary_parts.append("Heart rate trend supports the user's claimed sleep onset.")
        
        # Gaps
        if gap_analysis.get('total_gaps', 0) > 0:
            summary_parts.append(
                f"{gap_analysis.get('total_gaps', 0)} missing sleep records totaling "
                f"{gap_analysis.get('total_missing_minutes', 0)} minutes indicate temporary ring data loss."
            )
        
        # Root cause
        summary_parts.append(f"Root cause: {root_cause.get('primary_cause', 'N/A')}.")
        
        return " ".join(summary_parts) if summary_parts else "No significant issues detected."
    
    def generate_qa_remarks(self, analysis_results: Dict[str, Any]) -> str:
        """Generate QA remarks using AI"""
        if not self.client:
            # Use root cause engine's remarks
            from analyzers.root_cause_engine import RootCauseEngine
            engine = RootCauseEngine(analysis_results)
            return engine.generate_qa_remarks()
        
        prompt = f"""
Generate QA investigation remarks based on this sleep analysis:

{self._build_prompt(analysis_results)}

Generate 2-3 bullet points in the style of QA investigation remarks:
- Start with "Ring didn't capture..." for data issues
- Start with "Ignoring the initial awake..." for awake issues
- Start with "Heart rate trend supports..." for HR validation
- Start with "Production and Test Build match..." for build comparisons
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a QA engineer writing investigation remarks for sleep data issues."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.5
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI remarks generation failed: {e}")
            from analyzers.root_cause_engine import RootCauseEngine
            engine = RootCauseEngine(analysis_results)
            return engine.generate_qa_remarks()
