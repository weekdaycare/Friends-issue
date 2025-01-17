# -*- coding: utf-8 -*-
# author: https://github.com/BeaCox
from bs4 import BeautifulSoup
import os
import request
import json
import config
from concurrent.futures import ThreadPoolExecutor, as_completed

version = 'v2'
outputdir = version  # 输出文件结构变化时，更新输出路径版本
filenames = []
json_pool = []
email_list = []

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print("Created directory:", path)

def parse_issue_links(issues_page, data_pool=None, email_list=None):
    issues_soup = BeautifulSoup(issues_page, 'html.parser')
    try:
        if data_pool is not None:
            issues_linklist = issues_soup.find_all('pre')
            source = issues_linklist[0].text
            if "{" in source:
                source = json.loads(source)
                data_pool.append(source)

        if email_list is not None:
            mail_link = issues_soup.find('a', href=lambda x: x and x.startswith('mailto:'))
            if mail_link:
                mail_value = mail_link['href'].replace('mailto:', '')
                email_list.append(mail_value)
    except Exception:
        pass

def fetch_issues(repo, parameter, sort, label=None, data_pool=None, email_list=None):
    with ThreadPoolExecutor() as executor:
        for number in range(1, 100):
            print('Page:', number)
            url = f'https://api.github.com/repos/{repo}/issues'
            params = {
                'state': 'open',
                'page': number,
                'per_page': 30
            }
            if parameter:
                params['labels'] = parameter
            if sort:
                params['sort'] = sort
            if label:
                params['labels'] = label
            print('Parsing:', url)

            issues = request.get_json(url, params)

            if not issues:
                print('> End of issues')
                break

            future_to_issue = {executor.submit(request.get_data, issue['html_url']): issue for issue in issues}
            for future in as_completed(future_to_issue):
                issues_page = future.result()
                if issues_page:
                    parse_issue_links(issues_page, data_pool, email_list)

def github_issues(json_pool):
    print('\n------- GitHub Issues Start ----------')
    cfg = config.load()
    filter = cfg['issues']
    subscribe = cfg['rss_subscribe']['enable']

    if subscribe:
        fetch_issues(filter["repo"], parameter=None, sort=None, label='subscribe', email_list=email_list)

    if not filter["groups"]:
        data_pool = []
        filenames.append("data")
        parameter = filter["label"] if filter["label"] else ''
        fetch_issues(filter["repo"], parameter, filter["sort"], data_pool=data_pool)
        json_pool.append(data_pool)
    else:
        for group in filter["groups"]:
            print('Start of group:', group)
            data_pool = []
            filenames.append(group)
            parameter = filter["label"] if filter["label"] else ''
            fetch_issues(filter["repo"], parameter, filter["sort"], label=group, data_pool=data_pool)
            json_pool.append(data_pool)
            print("End of group:", group)

    print('------- GitHub Issues End ----------\n')

def save_json_files():
    mkdir(outputdir)
    for i, filename in enumerate(filenames):
        full_path = f'{outputdir}/{filename}.json'
        with open(full_path, 'w', encoding='utf-8') as file_obj:
            data = {'version': version, 'content': json_pool[i]}
            json.dump(data, file_obj, ensure_ascii=False, indent=2)

    # 删除重复邮件地址
    unique_emails = list(set(email_list))
    email_data = {"emails": unique_emails}
    with open(f'{outputdir}/subscribe.json', 'w', encoding='utf-8') as file_obj:
        json.dump(email_data, file_obj, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    github_issues(json_pool)
    save_json_files()
