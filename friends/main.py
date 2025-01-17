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
baselink = 'https://github.com/'

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print("Created directory:", path)

def parse_issue_links(issues_page, data_pool=None, email_list=None):
    issues_soup = BeautifulSoup(issues_page, 'html.parser')
    if data_pool is not None:
        try:
            issues_linklist = issues_soup.find_all('pre')
            source = issues_linklist[0].text
            if "{" in source:
                source = json.loads(source)
                data_pool.append(source)
        except Exception:
            pass

    if email_list is not None:
        try:
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
            url = f'https://github.com/{repo}/issues?page={number}&q=is%3Aopen'
            if parameter:
                url += parameter
            if sort:
                url += f'+sort%3A{sort}'
            if label:
                url += f'+label%3A{label}'
            print('Parsing:', url)

            github = request.get_data(url)
            soup = BeautifulSoup(github, 'html.parser')
            main_content = soup.find_all('ul', {'class': 'ListView-module__ul--vMLEZ'})

            if not main_content:
                print('> End of issues')
                break

            linklist = main_content[0].find_all('a', {'class': 'Title-module__anchor--SyQM6'})
            if not linklist:
                print('> End of links')
                break

            future_to_url = {executor.submit(request.get_data, baselink + item['href']): item for item in linklist}
            for future in as_completed(future_to_url):
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
        parameter = f'+label%3A{filter["label"]}' if filter["label"] else ''
        fetch_issues(filter["repo"], parameter, filter["sort"], data_pool=data_pool)
        json_pool.append(data_pool)
    else:
        for group in filter["groups"]:
            print('Start of group:', group)
            data_pool = []
            filenames.append(group)
            parameter = f'+label%3A{filter["label"]}' if filter["label"] else ''
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
