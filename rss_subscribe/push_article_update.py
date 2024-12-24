import logging
import requests
import re
from friend_circle_lite.get_info import check_feed, parse_feed
import json
import os

# 标准化的请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

def extract_emails(api_url):
    """
    从给定的 JSON API URL 获取邮箱地址。

    参数：
    api_url (str): 包含邮箱地址的 JSON 文件的 URL。

    返回：
    dict: 包含所有提取的邮箱地址的字典。
    {
        "emails": [
            "3162475700@qq.com"
        ]
    }
    """
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        logging.error(f"无法获取 GitHub issues 数据，错误信息: {e}")
        return None

def get_latest_articles_from_link(url, count=5, last_articles_path="./rss_subscribe/last_articles.json"):
    """
    从指定链接获取最新的文章数据并与本地存储的上次的文章数据进行对比。

    参数：
    url (str): 用于获取文章数据的链接。
    count (int): 获取文章数的最大数。如果小于则全部获取，如果文章数大于则只取前 count 篇文章。

    返回：
    list: 更新的文章列表，如果没有更新的文章则返回 None。
    """
    # 本地存储上次文章数据的文件
    local_file = last_articles_path
    
    # 检查和解析 feed
    session = requests.Session()
    feed_type, feed_url = check_feed(url, session)
    if feed_type == 'none':
        logging.error(f"无法获取 {url} 的文章数据")
        return None

    # 获取最新的文章数据
    latest_data = parse_feed(feed_url, session, count)
    latest_articles = latest_data['articles']
    logging.info(f"获取到的文章数量: {len(latest_articles)}")

    # 读取本地存储的上次的文章数据
    if os.path.exists(local_file):
        with open(local_file, 'r', encoding='utf-8') as file:
            try:
                last_data = json.load(file)
            except json.JSONDecodeError:
                logging.error("JSON 解码错误，使用空数据")
                last_data = {'articles': [], 'fail_count': 0}
    else:
        last_data = {'articles': [], 'fail_count': 0}

    last_articles = last_data.get('articles', [])
    fail_count = last_data.get('fail_count', 0)
    logging.info(f"本地存储的文章数量: {len(last_articles)}")

    # 找到更新的文章
    updated_articles = []
    last_titles = {article['link'] for article in last_articles}

    for article in latest_articles:
        if article['link'] not in last_titles:
            updated_articles.append(article)

    logging.info(f"从 {url} 获取到 {len(latest_articles)} 篇文章，其中 {len(updated_articles)} 篇为新文章")

    # 更新 fail_count 逻辑
    if len(latest_articles) == 0:
        fail_count += 1
    else:
        fail_count = 0

    # 判断是否更新本地存储
    if fail_count > 3 or len(latest_articles) > 0:
        # 更新本地存储的文章数据
        logging.info(f"准备写入文件: {local_file}")
        with open(local_file, 'w', encoding='utf-8') as file:
            json.dump({'articles': latest_articles, 'fail_count': fail_count}, file, ensure_ascii=False, indent=4)
        logging.info("文件写入成功")
    else:
                logging.info(f"从 {url} 获取到文章数量为0的次数: {zero_count}，未达到更新阈值，不更新本地存储")

    # 如果有更新的文章，返回这些文章，否则返回 None
    return updated_articles if updated_articles else None

