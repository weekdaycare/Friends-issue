import os
import re
import json
import requests

# 从环境变量获取配置
repo = os.getenv('GITHUB_REPOSITORY')
issue_number = os.getenv('ISSUE_NUMBER')
token = os.getenv('GITHUB_TOKEN')

# 设置请求头
headers = {'Authorization': f'token {token}'}

def get_issue_body(repo, issue_number):
    url = f'https://api.github.com/repos/{repo}/issues/{issue_number}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 自动处理HTTP错误
    return response.json()

def modify_label(repo, issue_number, add_label=None, remove_label=None):
    if add_label:
        url = f'https://api.github.com/repos/{repo}/issues/{issue_number}/labels'
        response = requests.post(url, headers=headers, json={"labels": [add_label]})
        response.raise_for_status()
    
    if remove_label:
        url = f'https://api.github.com/repos/{repo}/issues/{issue_number}/labels/{remove_label}'
        response = requests.delete(url, headers=headers)
        response.raise_for_status()

def has_email(body):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    return re.search(email_pattern, body) is not None

def main():
    issue_data = get_issue_body(repo, issue_number)
    body = issue_data.get('body', '')
    labels = {label['name'] for label in issue_data.get('labels', [])}  # 使用集合提高查找效率

    if has_email(body) and 'subscribe' not in labels:
        modify_label(repo, issue_number, add_label='subscribe')
        print(f"Issue #{issue_number} labeled with 'subscribe'.")
    elif not has_email(body) and 'subscribe' in labels:
        modify_label(repo, issue_number, remove_label='subscribe')
        print(f"'subscribe' label removed from issue #{issue_number}.")

if __name__ == "__main__":
    main()
