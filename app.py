from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
import re
from collections import Counter

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# JIRA API Configuration
JIRA_BASE_URL = os.getenv('JIRA_BASE_URL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')


def get_jira_issues():
    """
    Fetch issues from JIRA API
    Returns a list of issues with their details
    """
    # JQL query to get Epics, User Stories, Bugs, and Usability Bugs
    jql_query = 'type in ("Epic", "User Story") ORDER BY created DESC'

    # JIRA API endpoint for searching issues
    api_endpoint = f"{JIRA_BASE_URL}/rest/api/2/search"

    # Setting up authentication and headers
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Parameters for the API request
    params = {
        "jql": jql_query,
        "maxResults": 100,  # Adjust as needed
        "fields": "summary,description,issuetype,key"
    }

    try:
        response = requests.get(api_endpoint, auth=auth, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get('issues', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching JIRA issues: {e}")
        return []


def preprocess_text(text):
    """Simple text preprocessing"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and keep only alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_text_features(text):
    """Extract features from text - in this case, word frequency"""
    words = preprocess_text(text).split()
    return Counter(words)


def calculate_similarity(vec1, vec2):
    """Calculate similarity between two Counter objects using cosine similarity"""
    # Get all unique words
    all_words = set(vec1.keys()) | set(vec2.keys())

    # Calculate dot product
    dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in all_words)

    # Calculate magnitudes
    mag1 = sum(val ** 2 for val in vec1.values()) ** 0.5
    mag2 = sum(val ** 2 for val in vec2.values()) ** 0.5

    # Avoid division by zero
    if mag1 * mag2 == 0:
        return 0

    return dot_product / (mag1 * mag2)


def check_for_duplicates(new_requirement):
    """
    Check for similar requirements in JIRA issues
    Returns a list of similar issues sorted by similarity score
    """
    issues = get_jira_issues()
    if not issues:
        return []

    # Extract summaries and descriptions
    new_req_features = get_text_features(new_requirement)

    similar_issues = []

    for issue in issues:
        summary = issue['fields'].get('summary', '')
        description = issue['fields'].get('description', '') or ''
        # Combine summary and description for better matching
        issue_text = f"{summary} {description}"
        issue_features = get_text_features(issue_text)

        # Calculate similarity
        similarity = calculate_similarity(new_req_features, issue_features)

        if similarity > 0.25:  # Lower threshold for this simpler approach
            similar_issues.append({
                'key': issue['key'],
                'summary': issue['fields'].get('summary', ''),
                'type': issue['fields']['issuetype']['name'],
                'link': f"{JIRA_BASE_URL}/browse/{issue['key']}",
                'similarity': float(similarity)
            })

    # Sort by similarity score (descending)
    similar_issues.sort(key=lambda x: x['similarity'], reverse=True)
    return similar_issues


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check-duplicates', methods=['POST'])
def check_duplicates():
    requirement = request.form.get('requirement', '')
    if not requirement:
        return jsonify({'error': 'No requirement provided'}), 400

    similar_issues = check_for_duplicates(requirement)
    return jsonify({'similar_issues': similar_issues})


if __name__ == '__main__':
    app.run(debug=True)