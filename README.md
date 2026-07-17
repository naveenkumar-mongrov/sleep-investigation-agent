# Sleep Investigation AI Agent

An AI-powered tool for analyzing sleep data from Ring devices. This agent helps QA engineers and developers identify sleep tracking issues, compare data across builds, and determine root causes of discrepancies.

## Features

- **JSON Parsing**: Extracts sleep records, heart rate, and activity data from Ring JSON files
- **Sleep Stage Mapping**: Classifies sleep stages (Deep, Light, REM, Awake)
- **Missing Record Detection**: Identifies gaps in sleep data capture
- **Initial Awake Analysis**: Detects and handles initial awake periods before sleep
- **Heart Rate Validation**: Validates sleep claims using HR trends
- **Nap Detection**: Identifies potential nap events
- **Build Comparison**: Compares JSON, Production, and Test build data
- **Root Cause Engine**: Classifies issues and determines root cause
- **AI-Powered Summaries**: Generates human-readable investigation summaries using OpenAI GPT-4 (real-time)
- **Batch Processing**: Process 100+ users in parallel with AI analysis
- **Report Generation**: Exports Excel and GitHub issue formats

## Sleep Stage Mapping

- **1**: Deep Sleep
- **2**: Light Sleep
- **3**: REM Sleep
- **Everything else**: Awake

## Installation

### Option 1: Deploy as Website (Recommended - No Installation Required)

The easiest way to use this tool is to deploy it to Streamlit Cloud. See [deploy_instructions.md](deploy_instructions.md) for details.

**Quick Start:**
1. Push this code to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub and deploy
4. Access your app at `https://your-app-name.streamlit.app`

### Option 2: Local Installation

1. Clone the repository:
```bash
cd C:\Users\navee\CascadeProjects\sleep-investigation-agent
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note:** On Windows, you may need Visual Studio Build Tools to compile numpy/pandas. If installation fails, use Anaconda or deploy to Streamlit Cloud instead.

## Usage

### Running the Application (Local)

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Running the Application (Website)

Once deployed to Streamlit Cloud, simply access the URL provided (e.g., `https://your-app-name.streamlit.app`)

### Using the Tool

#### Single User Analysis

1. **Upload Ring JSON**: Select and upload a Ring JSON file
2. **Enter User Claim**: Input user-reported sleep details
   - Sleep Start Time (e.g., 11:20 PM)
   - Wake Time (e.g., 7:10 AM)
   - Awake During Sleep (optional)
   - Nap (optional)
   - Additional Remarks (optional)
3. **Enter Production Build Data**: Input sleep metrics from production build
   - Sleep Start/End
   - Deep, Light, REM, Awake durations
4. **Enter Test Build Data**: Input sleep metrics from test build
   - Sleep Start/End
   - Deep, Light, REM, Awake durations
5. **Click Analyze**: Run the analysis and view results

#### Batch Analysis (100+ Users)

1. **Upload Multiple JSON Files**: Select all Ring JSON files to process
2. **Upload Claims File (Optional)**: Upload a JSON file with user claims, production, and test data
3. **Generate Claims Template**: Click to get a template for the claims file
4. **Click Process Batch**: Process all users with real-time AI analysis

**Claims File Format:**
```json
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
```

**Batch Processing Features:**
- Parallel processing with configurable workers (default: 4)
- Real-time AI analysis for each user
- Summary statistics across all users
- Root cause distribution analysis
- Issue breakdown (application issues, initial awake, gaps, HR validation)
- Excel export with detailed results for each user

#### External Data Sources (Google Sheets + GitHub)

The tool can automatically fetch data from external sources:

**Google Sheets Integration:**
- Fetch user claims data directly from Google Sheets
- Configure spreadsheet ID and sheet name
- Map columns to claim fields
- Requires Google Sheets API key

**GitHub Integration:**
- Fetch JSON files directly from GitHub repositories
- Support for public and private repositories
- Specify repository owner, name, and path
- Automatic file download and processing

**Configuration:**
Set up external data sources in `config.py`:
```python
# Google Sheets
GOOGLE_SHEETS_API_KEY = "your-api-key"
GOOGLE_SHEETS_ID = "spreadsheet-id-from-url"
GOOGLE_SHEETS_SHEET_NAME = "Sheet1"

# GitHub
GITHUB_TOKEN = "your-github-token"  # Optional for private repos
GITHUB_OWNER = "repository-owner"
GITHUB_REPO = "repository-name"
GITHUB_PATH = "path/to/json/files"
```

**Using External Data Sources:**
1. Select "Google Sheets + GitHub" in Batch Analysis tab
2. Configure Google Sheets ID and sheet name
3. Configure GitHub repository details
4. Click "Process Batch" to automatically fetch and analyze
5. Data is fetched, processed with AI, and results displayed

### AI Features (Optional)

To enable AI-powered summaries, enter your OpenAI API key in the sidebar configuration.

## Project Structure

```
sleep-investigation-agent/
├── analyzers/
│   ├── __init__.py
│   ├── json_parser.py          # JSON parsing and data extraction
│   ├── sleep_analyzer.py       # Sleep stage analysis
│   ├── gap_detector.py         # Missing record detection
│   ├── initial_awake_detector.py  # Initial awake period analysis
│   ├── hr_validator.py         # Heart rate validation
│   ├── nap_detector.py         # Nap event detection
│   ├── build_comparator.py     # Build comparison logic
│   └── root_cause_engine.py    # Root cause classification
├── ai/
│   ├── __init__.py
│   └── ai_investigator.py      # AI-powered summary generation
├── utils/
│   ├── __init__.py
│   └── report_generator.py     # Excel and text report generation
├── uploads/                    # Directory for uploaded JSON files
├── reports/                    # Directory for generated reports
├── examples/                   # Sample JSON files for reference
│   └── 9837_16Jul.json         # Example Ring JSON file
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Analysis Workflow

1. **JSON Parsing**: Extracts sleep records, HR, and activity data
2. **Sleep Analysis**: Calculates sleep metrics and stage distribution
3. **Gap Detection**: Identifies missing data intervals
4. **Initial Awake Detection**: Analyzes awake periods before sleep
5. **HR Validation**: Validates sleep claims using heart rate trends
6. **Nap Detection**: Identifies potential nap events
7. **Build Comparison**: Compares JSON vs Production vs Test data
8. **Root Cause Engine**: Classifies the issue and determines root cause
9. **AI Summary**: Generates human-readable investigation summary (optional)
10. **Report Generation**: Creates Excel and GitHub issue formats

## Root Cause Classification

The tool can identify the following root causes:

- Ring missed sleep records
- Initial awake incorrectly considered
- Possible nap not detected
- JSON issue
- Production build issue
- Test build issue
- HR supports user claim
- HR does not support user claim
- No issue found

## Output

The tool generates:

- **Comprehensive Analysis Results**: Detailed breakdown of all findings
- **Root Cause Classification**: Primary cause and severity
- **QA-Ready Remarks**: Standardized investigation comments
- **Excel Report**: Multi-sheet Excel file with all data
- **GitHub Issue Format**: Ready-to-post GitHub issue text

## Example Output

```
USER CLAIM
-----------
Sleep Start: 11:20 PM
Wake Time: 7:10 AM

ANALYSIS
-----------
• Initial awake lasted 42 minutes.
• Ignoring initial awake, sleep starts at 11:18 PM.
• Matches user claim.
• Heart rate gradually reduced from 86 bpm to 63 bpm.
• Two missing sleep records (14 mins and 11 mins) indicate temporary ring capture loss.
• No nap events detected.

ROOT CAUSE
-----------
Primary Cause: Initial awake misclassification with temporary ring capture gaps.
Is Application Issue: No

QA REMARKS
-----------
Ignoring the initial awake period aligns with the user's reported sleep time.
Heart rate trend supports the user's claimed sleep onset.
Ring didn't capture sleep data. Not an application issue.
```

## Technology Stack

- **Backend**: Python 3.12
- **Frontend**: Streamlit
- **Data Processing**: Pandas
- **AI**: OpenAI GPT-4 (optional)
- **Export**: Excel (openpyxl)

## Requirements

- Python 3.12 or higher
- pip package manager

## License

Internal QA Tool - For team use only.

## Support

For issues or questions, contact the development team.
