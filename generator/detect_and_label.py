import os
import request
import requests
import re
import json

repo = os.getenv('GITHUB_REPOSITORY')
issue_number = os.getenv('ISSUE_NUMBER')
token = os.getenv('GITHUB_TOKEN')

def get_issue_body(repo, issue_number):
    url = f'https://api.github.com/repos/{repo}/issues/{issue_number}'
    headers = {'Authorization': f'token {token}'}
    response = request.get_data(url)
    if response == 'error':
        raise Exception('HTTP 404 Error')
    return json.loads(response)

def modify_label(repo, issue_number, add_label=None, remove_label=None):
    headers = {'Authorization': f'token {token}'}
    
    if add_label:
        url = f'https://api.github.com/repos/{repo}/issues/{issue_number}/labels'
        response = requests.post(url, headers=headers, json={"labels": [add_label]})
        response.raise_for_status()
    
    if remove_label:
        url = f'https://api.github.com/repos/{repo}/issues/{issue_number}/labels/{remove_label}'
        response = requests.delete(url, headers=headers)
        response.raise_for_status()

def main():
    issue_data = get_issue_body(repo, issue_number)
    body = issue_data.get('body', '')
    labels = [label['name'] for label in issue_data.get('labels', [])]
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
    has_email = re.search(email_pattern, body)
    has_subscribe_label = 'subscribe' in labels

    if has_email and not has_subscribe_label:
        modify_label(repo, issue_number, add_label='subscribe')
        print(f"Issue #{issue_number} labeled with 'subscribe'.")
    elif not has_email and has_subscribe_label:
        modify_label(repo, issue_number, remove_label='subscribe')
        print(f"'subscribe' label removed from issue #{issue_number}.")

if __name__ == "__main__":
    main()
