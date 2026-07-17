"""
Sleep Investigation AI Agent - Streamlit Application
Main application for sleep data analysis
"""

import streamlit as st
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzers import (
    JSONParser, SleepAnalyzer, GapDetector, InitialAwakeDetector,
    HRValidator, NapDetector, BuildComparator, RootCauseEngine, BatchProcessor
)
from utils import ReportGenerator
from ai import AIInvestigator
import config


# Page configuration
st.set_page_config(
    page_title="Sleep Investigation AI Agent",
    page_icon="😴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    st.markdown('<div class="main-header">😴 Sleep Investigation AI Agent</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        # OpenAI API Key (optional - uses config.py by default)
        api_key = st.text_input(
            "OpenAI API Key (Optional)",
            type="password",
            value=config.OPENAI_API_KEY,
            help="Enter for AI-powered summaries (configured in config.py)"
        )
        
        st.markdown("---")
        st.markdown("### Instructions")
        st.markdown("""
        **Single Analysis:**
        1. Upload Ring JSON file
        2. Enter user-reported sleep details
        3. Enter Production build data
        4. Enter Test build data
        5. Click Analyze
        
        **Batch Analysis:**
        1. Upload multiple JSON files
        2. Upload claims JSON file (optional)
        3. Click Process Batch
        """)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Single Analysis", "Batch Analysis", "About"])
    
    with tab1:
        analyze_page(api_key)
    
    with tab2:
        batch_analysis_page(api_key)
    
    with tab3:
        about_page()


def analyze_page(api_key):
    """Main analysis page"""
    
    # File upload
    st.markdown('<div class="section-header">1. Upload Ring JSON</div>', unsafe_allow_html=True)
    json_file = st.file_uploader("Upload Ring JSON file", type=['json'])
    
    if json_file:
        # Save uploaded file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        json_path = os.path.join(upload_dir, json_file.name)
        
        with open(json_path, 'wb') as f:
            f.write(json_file.getbuffer())
        
        st.success(f"File uploaded: {json_file.name}")
    
    # User claim
    st.markdown('<div class="section-header">2. User Reported Sleep Details</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        user_sleep_start = st.text_input("Sleep Start Time", placeholder="e.g., 11:20 PM")
    with col2:
        user_wake_time = st.text_input("Wake Time", placeholder="e.g., 7:10 AM")
    
    user_awake_during = st.text_input("Awake During Sleep (Optional)", placeholder="e.g., 2 times")
    user_nap = st.text_input("Nap (Optional)", placeholder="e.g., 2:15 PM - 2:50 PM")
    user_remarks = st.text_area("Additional Remarks (Optional)", placeholder="Any additional information...")
    
    # Production build
    st.markdown('<div class="section-header">3. Production Build Data</div>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        prod_sleep_start = st.text_input("Production Sleep Start", placeholder="e.g., 11:18 PM")
        prod_sleep_end = st.text_input("Production Sleep End", placeholder="e.g., 7:08 AM")
        prod_deep = st.text_input("Production Deep Sleep (mins)", placeholder="e.g., 90")
    with col4:
        prod_light = st.text_input("Production Light Sleep (mins)", placeholder="e.g., 240")
        prod_rem = st.text_input("Production REM Sleep (mins)", placeholder="e.g., 105")
        prod_awake = st.text_input("Production Awake (mins)", placeholder="e.g., 15")
    
    # Test build
    st.markdown('<div class="section-header">4. Test Build Data</div>', unsafe_allow_html=True)
    
    col5, col6 = st.columns(2)
    with col5:
        test_sleep_start = st.text_input("Test Sleep Start", placeholder="e.g., 11:18 PM")
        test_sleep_end = st.text_input("Test Sleep End", placeholder="e.g., 7:08 AM")
        test_deep = st.text_input("Test Deep Sleep (mins)", placeholder="e.g., 90")
    with col6:
        test_light = st.text_input("Test Light Sleep (mins)", placeholder="e.g., 240")
        test_rem = st.text_input("Test REM Sleep (mins)", placeholder="e.g., 105")
        test_awake = st.text_input("Test Awake (mins)", placeholder="e.g., 15")
    
    # Analyze button
    st.markdown("---")
    analyze_button = st.button("🔍 Analyze Sleep Data", type="primary", use_container_width=True)
    
    if analyze_button:
        if not json_file:
            st.error("Please upload a Ring JSON file")
            return
        
        if not user_sleep_start or not user_wake_time:
            st.error("Please enter user sleep start and wake time")
            return
        
        # Run analysis
        with st.spinner("Analyzing sleep data..."):
            try:
                analysis_results = run_analysis(
                    json_path,
                    user_sleep_start,
                    user_wake_time,
                    user_awake_during,
                    user_nap,
                    user_remarks,
                    {
                        'sleep_start': prod_sleep_start,
                        'sleep_end': prod_sleep_end,
                        'deep': prod_deep,
                        'light': prod_light,
                        'rem': prod_rem,
                        'awake': prod_awake
                    },
                    {
                        'sleep_start': test_sleep_start,
                        'sleep_end': test_sleep_end,
                        'deep': test_deep,
                        'light': test_light,
                        'rem': test_rem,
                        'awake': test_awake
                    },
                    api_key
                )
                
                display_results(analysis_results)
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.exception(e)


def run_analysis(json_path, user_sleep_start, user_wake_time, user_awake, user_nap, user_remarks,
                 production_data, test_data, api_key):
    """Run the complete analysis pipeline"""
    
    # Parse JSON
    parser = JSONParser(json_path)
    parsed_data = parser.parse_all()
    
    # Sleep analysis
    sleep_analyzer = SleepAnalyzer(parsed_data['sleep_records'])
    sleep_analysis = sleep_analyzer.analyze_sleep_periods()
    
    # Claim comparison
    claim_comparison = sleep_analyzer.compare_with_claim(user_sleep_start, user_wake_time)
    
    # Gap detection
    gap_detector = GapDetector(parsed_data['sleep_records'])
    gap_analysis = gap_detector.get_gap_summary()
    
    # Initial awake detection
    awake_detector = InitialAwakeDetector(parsed_data['sleep_records'])
    initial_awake = awake_detector.detect_initial_awake()
    initial_awake_comparison = awake_detector.compare_with_claim(user_sleep_start)
    
    # HR validation
    hr_validator = HRValidator(parsed_data['heart_rate'])
    hr_validation = hr_validator.validate_sleep_claim(user_sleep_start)
    
    # Nap detection
    nap_detector = NapDetector(parsed_data['sleep_records'], parsed_data['heart_rate'], parsed_data['activity'])
    naps = nap_detector.detect_naps()
    nap_analysis = nap_detector.check_nap_in_builds(production_data, test_data)
    
    # Build comparison
    build_comparator = BuildComparator(sleep_analysis, production_data, test_data)
    build_comparison = build_comparator.compare_all()
    build_comparison['comparison_table'] = build_comparator.generate_comparison_table()
    
    # Root cause analysis
    all_results = {
        'user_claim': {
            'sleep_start': user_sleep_start,
            'wake_time': user_wake_time,
            'awake_during': user_awake,
            'nap': user_nap,
            'remarks': user_remarks
        },
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
    
    # AI investigation
    ai_investigator = AIInvestigator(api_key)
    ai_summary = ai_investigator.generate_investigation_summary(all_results)
    ai_qa_remarks = ai_investigator.generate_qa_remarks(all_results)
    
    # Compile final results
    final_results = {
        'user_claim': all_results['user_claim'],
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
        'ai_qa_remarks': ai_qa_remarks
    }
    
    return final_results


def display_results(results):
    """Display analysis results"""
    
    st.markdown('<div class="section-header">📊 Analysis Results</div>', unsafe_allow_html=True)
    
    # AI Summary
    if results.get('ai_summary'):
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("### 🤖 AI Investigation Summary")
        st.write(results['ai_summary'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # User Claim vs JSON
    st.markdown("### 👤 User Claim vs JSON")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("User Claim", results['user_claim']['sleep_start'])
    with col2:
        st.metric("JSON Sleep Start", results['claim_comparison'].get('json_sleep_start', 'N/A'))
    with col3:
        st.metric("JSON (Ignored Awake)", results['claim_comparison'].get('json_sleep_start_ignored', 'N/A'))
    
    # Initial Awake
    initial_awake = results['initial_awake']
    if initial_awake.get('has_initial_awake'):
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown(f"**Initial Awake Detected:** {initial_awake.get('duration_minutes', 0)} minutes")
        st.markdown(f"Ignoring initial awake, sleep starts at: {initial_awake.get('ignoring_initial_awake', 'N/A')}")
        st.markdown(f"Matches user claim: {'✅ Yes' if initial_awake.get('ignored_match') else '❌ No'}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # HR Validation
    hr_val = results['hr_validation']
    if hr_val.get('supports_sleep'):
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("### ❤️ Heart Rate Validation")
        st.write("✅ Heart rate trend supports the user's claimed sleep onset")
        st.write(f"HR Trend: {hr_val.get('hr_trend', 'N/A')}")
        st.write(f"Classification: {hr_val.get('classification', 'N/A')}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Gap Analysis
    gap_analysis = results['gap_analysis']
    if gap_analysis.get('total_gaps', 0) > 0:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown(f"### ⚠️ Missing Sleep Records: {gap_analysis.get('total_gaps', 0)}")
        st.write(f"Total missing time: {gap_analysis.get('total_missing_minutes', 0)} minutes")
        st.write("Classification: Ring Data Loss")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Nap Detection
    nap_analysis = results['nap_analysis']
    if nap_analysis.get('total_naps', 0) > 0:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown(f"### 😴 Possible Naps Detected: {nap_analysis.get('total_naps', 0)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Build Comparison
    st.markdown("### 🔧 Build Comparison")
    comparison_table = results['build_comparison'].get('comparison_table', [])
    if comparison_table:
        st.dataframe(comparison_table, use_container_width=True)
    
    # Root Cause
    root_cause = results['root_cause']
    st.markdown("### 🎯 Root Cause Analysis")
    
    if root_cause.get('is_application_issue'):
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.markdown(f"**Primary Cause:** {root_cause.get('primary_cause', 'N/A')}")
        st.markdown(f"**Verdict:** {root_cause.get('verdict', 'N/A')}")
        st.markdown("**⚠️ Application Issue Detected**")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown(f"**Primary Cause:** {root_cause.get('primary_cause', 'N/A')}")
        st.markdown(f"**Verdict:** {root_cause.get('verdict', 'N/A')}")
        st.markdown("**✅ No Application Issue**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # QA Remarks
    st.markdown("### 📝 QA Remarks")
    st.markdown(results['qa_remarks'])
    
    # Recommendation
    st.markdown("### 💡 Recommendation")
    st.info(results.get('recommendation', 'N/A'))
    
    # Export options
    st.markdown("---")
    st.markdown("### 📥 Export Report")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Excel Report"):
            report_gen = ReportGenerator()
            excel_path = report_gen.generate_excel_report(results)
            st.success(f"Excel report generated: {excel_path}")
    
    with col2:
        if st.button("Copy GitHub Issue"):
            report_gen = ReportGenerator()
            github_issue = report_gen.generate_github_issue(results)
            st.text_area("GitHub Issue", github_issue, height=200)


def batch_analysis_page(api_key):
    """Batch analysis page for processing 100+ users"""
    
    st.markdown('<div class="section-header">📦 Batch Analysis (100+ Users)</div>', unsafe_allow_html=True)
    
    # Data source selection
    st.markdown("### Data Source")
    data_source = st.radio(
        "Select data source:",
        ["Manual Upload", "Google Sheets + GitHub"],
        help="Choose between manual file upload or automatic fetch from external sources"
    )
    
    if data_source == "Manual Upload":
        # File uploads
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Upload JSON Files")
            json_files = st.file_uploader(
                "Upload multiple Ring JSON files",
                type=['json'],
                accept_multiple_files=True,
                help="Select all JSON files to process"
            )
        
        with col2:
            st.markdown("### Upload Claims File (Optional)")
            claims_file = st.file_uploader(
                "Upload claims JSON file",
                type=['json'],
                help="Optional: Upload a JSON file with user claims, production, and test data"
            )
    else:
        # External source configuration
        st.markdown("### Google Sheets Configuration")
        google_sheets_id = st.text_input(
            "Google Sheets Spreadsheet ID",
            value=config.GOOGLE_SHEETS_ID,
            help="Found in your Google Sheets URL: docs.google.com/spreadsheets/d/[SHEET_ID]/edit"
        )
        sheet_name = st.text_input(
            "Sheet Name",
            value=config.GOOGLE_SHEETS_SHEET_NAME,
            help="Name of the sheet to fetch data from"
        )
        google_api_key = st.text_input(
            "Google Sheets API Key (Optional)",
            value=config.GOOGLE_SHEETS_API_KEY,
            type="password",
            help="Leave empty to use config.py value"
        )
        
        st.markdown("### GitHub Configuration")
        col1, col2 = st.columns(2)
        with col1:
            github_owner = st.text_input(
                "GitHub Repository Owner",
                value=config.GITHUB_OWNER,
                help="e.g., 'octocat' for https://github.com/octocat/repo"
            )
            github_repo = st.text_input(
                "GitHub Repository Name",
                value=config.GITHUB_REPO,
                help="e.g., 'Hello-World' for https://github.com/octocat/Hello-World"
            )
        with col2:
            github_path = st.text_input(
                "Path to JSON Files (Optional)",
                value=config.GITHUB_PATH,
                help="e.g., 'data/json' if files are in a subdirectory"
            )
            github_token = st.text_input(
                "GitHub Token (Optional - for private repos)",
                value=config.GITHUB_TOKEN,
                type="password",
                help="Leave empty for public repositories"
            )
        
        json_files = None
        claims_file = None
    
    # Generate claims template
    if st.button("📋 Generate Claims Template"):
        processor = BatchProcessor(api_key)
        template_path = processor.generate_claims_template()
        st.success(f"Template generated: {template_path}")
        st.code("""
[
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
        """, language='json')
    
    # Process batch button
    st.markdown("---")
    process_button = st.button("🚀 Process Batch", type="primary", use_container_width=True)
    
    if process_button:
        if data_source == "Manual Upload":
            if not json_files:
                st.error("Please upload at least one JSON file")
                return
            
            # Save uploaded files
            upload_dir = "uploads/batch"
            os.makedirs(upload_dir, exist_ok=True)
            
            json_paths = []
            for json_file in json_files:
                file_path = os.path.join(upload_dir, json_file.name)
                with open(file_path, 'wb') as f:
                    f.write(json_file.getbuffer())
                json_paths.append(file_path)
            
            # Save claims file if provided
            claims_path = None
            if claims_file:
                claims_path = os.path.join(upload_dir, claims_file.name)
                with open(claims_path, 'wb') as f:
                    f.write(claims_file.getbuffer())
            
            # Process batch
            with st.spinner(f"Processing {len(json_paths)} users with AI analysis..."):
                try:
                    processor = BatchProcessor(api_key)
                    
                    if claims_path:
                        # Process with claims file
                        batch_results = processor.process_batch_from_directory(
                            upload_dir,
                            claims_path,
                            max_workers=config.MAX_WORKERS
                        )
                    else:
                        # Process without claims (empty data)
                        user_claims = [{}] * len(json_paths)
                        production_data = [{}] * len(json_paths)
                        test_data = [{}] * len(json_paths)
                        user_ids = [os.path.basename(f) for f in json_paths]
                        
                        batch_results = processor.process_batch(
                            json_paths,
                            user_claims,
                            production_data,
                            test_data,
                            user_ids,
                            max_workers=config.MAX_WORKERS
                        )
                    
                    display_batch_results(batch_results, processor)
                    
                except Exception as e:
                    st.error(f"Batch processing failed: {str(e)}")
                    st.exception(e)
        else:
            # External sources
            if not google_sheets_id and not (github_owner and github_repo):
                st.error("Please provide either Google Sheets ID or GitHub repository details")
                return
            
            with st.spinner("Fetching data from external sources and processing with AI analysis..."):
                try:
                    processor = BatchProcessor(
                        api_key,
                        google_api_key or config.GOOGLE_SHEETS_API_KEY,
                        github_token or config.GITHUB_TOKEN
                    )
                    
                    batch_results = processor.process_from_external_sources(
                        google_sheets_id=google_sheets_id if google_sheets_id else None,
                        github_owner=github_owner if github_owner else None,
                        github_repo=github_repo if github_repo else None,
                        github_path=github_path,
                        sheet_name=sheet_name,
                        max_workers=config.MAX_WORKERS
                    )
                    
                    display_batch_results(batch_results, processor)
                    
                except Exception as e:
                    st.error(f"External data processing failed: {str(e)}")
                    st.exception(e)


def display_batch_results(batch_results, processor):
    """Display batch analysis results"""
    
    st.markdown('<div class="section-header">📊 Batch Analysis Results</div>', unsafe_allow_html=True)
    
    # Summary metrics
    summary = batch_results.get('summary', {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", batch_results.get('total_users', 0))
    with col2:
        st.metric("Processed", batch_results.get('processed', 0))
    with col3:
        st.metric("Errors", batch_results.get('errors', 0))
    with col4:
        st.metric("Success Rate", f"{batch_results.get('success_rate', 0):.1f}%")
    
    # Root cause distribution
    st.markdown("### 🎯 Root Cause Distribution")
    root_cause_dist = summary.get('root_cause_distribution', {})
    if root_cause_dist:
        cause_df = pd.DataFrame([
            {'Cause': cause, 'Count': count}
            for cause, count in root_cause_dist.items()
        ])
        st.dataframe(cause_df, use_container_width=True)
    else:
        st.info("No root cause data available")
    
    # Issue breakdown
    st.markdown("### ⚠️ Issue Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Application Issues", summary.get('application_issues', 0))
    with col2:
        st.metric("Initial Awake Issues", summary.get('initial_awake_issues', 0))
    with col3:
        st.metric("Gap Issues", summary.get('gap_issues', 0))
    with col4:
        st.metric("HR Supported Claims", summary.get('hr_supported_claims', 0))
    
    # Most common issue
    if summary.get('most_common_issue'):
        st.info(f"🔍 Most Common Issue: {summary['most_common_issue']}")
    
    # Detailed results table
    st.markdown("### 📋 Detailed Results")
    results_data = []
    for result in batch_results.get('results', []):
        if result['status'] == 'success':
            results_data.append({
                'User ID': result['user_id'],
                'Status': result['status'],
                'Sleep Start': result.get('claim_comparison', {}).get('json_sleep_start', 'N/A'),
                'Initial Awake': result.get('initial_awake', {}).get('has_initial_awake', False),
                'Gaps': result.get('gap_analysis', {}).get('total_gaps', 0),
                'HR Supports': result.get('hr_validation', {}).get('supports_sleep', False),
                'Root Cause': result.get('root_cause', {}).get('primary_cause', 'N/A'),
                'App Issue': result.get('root_cause', {}).get('is_application_issue', False),
                'AI Summary': result.get('ai_summary', 'N/A')[:50] + '...' if len(result.get('ai_summary', '')) > 50 else result.get('ai_summary', 'N/A')
            })
        else:
            results_data.append({
                'User ID': result['user_id'],
                'Status': result['status'],
                'Error': result.get('error', 'N/A')
            })
    
    results_df = pd.DataFrame(results_data)
    st.dataframe(results_df, use_container_width=True, height=400)
    
    # Export options
    st.markdown("---")
    st.markdown("### 📥 Export Results")
    
    if st.button("Generate Excel Report"):
        excel_path = processor.export_batch_results()
        st.success(f"Excel report generated: {excel_path}")
        
        # Provide download
        with open(excel_path, 'rb') as f:
            st.download_button(
                label="Download Excel Report",
                data=f,
                file_name=os.path.basename(excel_path),
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )


def about_page():
    """About page"""
    st.markdown('<div class="section-header">About Sleep Investigation AI Agent</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Overview
    The Sleep Investigation AI Agent is a comprehensive tool for analyzing sleep data from Ring devices. 
    It helps QA engineers and developers identify issues with sleep tracking, compare data across different builds,
    and determine the root cause of discrepancies.
    
    ### Features
    - **JSON Parsing**: Extracts sleep records, heart rate, and activity data from Ring JSON files
    - **Sleep Stage Mapping**: Classifies sleep stages (Deep, Light, REM, Awake)
    - **Missing Record Detection**: Identifies gaps in sleep data capture
    - **Initial Awake Analysis**: Detects and handles initial awake periods
    - **Heart Rate Validation**: Validates sleep claims using HR trends
    - **Nap Detection**: Identifies potential nap events
    - **Build Comparison**: Compares JSON, Production, and Test build data
    - **Root Cause Engine**: Classifies issues and determines root cause
    - **AI-Powered Summaries**: Generates human-readable investigation summaries
    - **Report Generation**: Exports Excel and GitHub issue formats
    
    ### Sleep Stage Mapping
    - **1**: Deep Sleep
    - **2**: Light Sleep
    - **3**: REM Sleep
    - **Everything else**: Awake
    
    ### Technology Stack
    - **Backend**: Python 3.12
    - **Frontend**: Streamlit
    - **Data Processing**: Pandas
    - **AI**: OpenAI GPT-4 (optional)
    - **Export**: Excel (openpyxl)
    
    ### Usage
    1. Upload a Ring JSON file
    2. Enter user-reported sleep details
    3. Enter Production build sleep data
    4. Enter Test build sleep data
    5. Click Analyze to generate the investigation report
    
    ### Output
    The tool generates:
    - Comprehensive analysis results
    - Root cause classification
    - QA-ready remarks
    - Excel report
    - GitHub issue format
    
    ### Root Cause Classification
    Possible root causes:
    - Ring missed sleep records
    - Initial awake incorrectly considered
    - Possible nap not detected
    - JSON issue
    - Production build issue
    - Test build issue
    - HR supports user claim
    - HR does not support user claim
    - No issue found
    """)


if __name__ == "__main__":
    main()
