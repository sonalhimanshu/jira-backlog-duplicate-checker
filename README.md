# JIRA Requirement Duplicate Checker

A Flask application that helps identify similar requirements in your JIRA project.

## Features

- Simple web interface to enter new requirements
- Searches existing JIRA issues for similar content
- Shows matching keywords between requirements
- Displays results in a clean, sortable table
- Links directly to JIRA issues

## Installation

1. Clone this repository:
   ```
   git clone [your-repository-url]
   cd jira-requirement-checker
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file with your JIRA credentials:
   ```
   JIRA_BASE_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   ```
   
   To create an API token, visit: https://id.atlassian.com/manage-profile/security/api-tokens

## Usage

1. Run the application:
   ```
   python app_keyword_based.py
   ```

2. Open your browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

3. Enter your requirement in the text box and click "Check for Duplicates"

## Troubleshooting

- **JIRA API Connection Issues**: Make sure your API token is correct and you have proper permissions
- **No Results**: Try using more specific keywords in your requirement
- **Application Won't Start**: Check that you've activated the virtual environment before running
