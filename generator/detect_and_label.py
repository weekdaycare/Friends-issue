import os
import requests
import re

repo = os.getenv('GITHUB_REPOSITORY')
issue_number = os.getenv('ISSUE_NUMBER')
token = os.getenv('GITHUB_TOKEN')

def get_issue_body(repo, issue_number):
    url = f'https://api.github.com/repos/{repo}/issues/{issue_number}'
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('body', '')

def label_issue(repo, issue_number, label):
    url = f'https://api.github.com/repos/{repo}/issues/{issue_number}/labels'
    headers = {'Authorization': f'token {token}'}
    response = requests.post(url, headers=headers, json={"labels": [label]})
    response.raise_for_status()

def main():
    body = get_issue_body(repo, issue_number)
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
    if re.search(email_pattern, body):
        label_issue(repo, issue_number, 'subscribe')
        print(f"Issue #{issue_number} labeled with 'subscribe'.")

if __name__ == "__main__":
    main()
