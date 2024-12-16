# 引入 check_feed 和 parse_feed 函数
from friend_circle_lite.get_info import fetch_and_process_data, sort_articles_by_time, marge_data_from_json_url, marge_errors_from_json_url, deal_with_large_data
from friend_circle_lite.get_conf import load_config
from rss_subscribe.push_article_update import get_latest_articles_from_link, extract_emails
from push_rss_update.send_email import send_emails

import logging
import json
import sys
import os

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# 爬虫部分内容
config = load_config("./config.yaml")
# 获取并强制转换为字符串
# 尝试从环境变量获取 FCL_REPO
fcl_repo = os.getenv('FCL_REPO')
if config["spider_settings"]["enable"]:
    logging.info("爬虫已启用")
    json_url = config['spider_settings'].get('json_url','')
    article_count = config['spider_settings']['article_count']
    expire_date = config['spider_settings']['expire_date'] 
    specific_RSS = config['specific_RSS']
    logging.info("正在从 {json_url} 中获取，每个博客获取 {article_count} 篇文章".format(json_url=json_url, article_count=article_count))
    result, lost_friends = fetch_and_process_data(json_url=json_url, specific_RSS=specific_RSS, count=article_count, expire_date=expire_date)
    if config["spider_settings"]["merge_result"]["enable"]:
        marge_json_url = config['spider_settings']["merge_result"]['merge_json_url']
        logging.info("合并数据功能开启，从 {marge_json_url} 中获取境外数据并合并".format(marge_json_url=marge_json_url + "/all.json"))
        result = marge_data_from_json_url(result, marge_json_url + "/all.json")
        lost_friends = marge_errors_from_json_url(lost_friends, marge_json_url + "/errors.json")
    logging.info("数据获取完毕，目前共有 {count} 位好友的动态，正在处理数据".format(count=len(result.get("article_data", []))))
    result = deal_with_large_data(result)

    with open("all.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with open("errors.json", "w", encoding="utf-8") as f:
        json.dump(lost_friends, f, ensure_ascii=False, indent=2)

if config["email_push"]["enable"] or config["rss_subscribe"]["enable"]:
    logging.info("推送功能已启用，正在准备推送，获取配置信息")
    email_settings = config["smtp"]
    email = email_settings["email"]
    server = email_settings["server"]
    port = email_settings["port"]
    use_tls = email_settings["use_tls"]
    password = os.getenv("SMTP_PWD")
    logging.info("SMTP 服务器信息：{server}:{port}".format(server=server, port=port))
    logging.info("密码：{pwd}************".format(pwd=password[:3]))

if config["email_push"]["enable"]:
    logging.info("邮件推送已启用")
    logging.info("抱歉，目前暂未实现功能")
    
if config["rss_subscribe"]["enable"]:
    logging.info("RSS 订阅推送已启用")

    # 提取 github_username 和 github_repo
    if fcl_repo:
        github_username, github_repo = fcl_repo.split('/')
    else:
        github_username = str(config["rss_subscribe"]["github_username"]).strip()
        github_repo = str(config["rss_subscribe"]["github_repo"]).strip()
    # 输出 github_username 和 github_repo
    logging.info("github_username: {github_username}".format(github_username=github_username))
    logging.info("github_repo: {github_repo}".format(github_repo=github_repo))
    
    your_blog_url = config["rss_subscribe"]["your_blog_url"]
    email_template = config["rss_subscribe"]["email_template"]
    # 获取网站信息
    website_title = config["rss_subscribe"]["website_info"]["title"]
    # 获取最近更新的文章
    latest_articles = get_latest_articles_from_link(
        url=your_blog_url,
        count=5,
        last_articles_path="./rss_subscribe/last_articles.json"
        )
    logging.info("获取到的最新文章为：{latest_articles}".format(latest_articles=latest_articles))
    if latest_articles == None:
        logging.info("无未进行推送的新文章")
    else:
        mail_url = f"https://raw.githubusercontent.com/{fcl_repo}/output/v2/subscribe.json"
        logging.info("正在从 {mail_url} 中获取订阅信息".format(mail_url=mail_url))
        email_list = extract_emails(mail_url)
        if email_list == None:
            logging.info("无邮箱列表，请检查您的订阅列表是否有订阅者或订阅格式是否正确")
            sys.exit(0)
        else:
            logging.info("获取到的邮箱列表为：{email_list}".format(email_list=email_list))
        # 循环latest_articles，发送邮件
        for article in latest_articles:
            template_data = {
                "title": article["title"],
                "summary": article["summary"],
                "published": article["published"],
                "link": article["link"],
                "website_title": website_title,
                "github_issue_url": f"https://github.com/{fcl_repo}/issues?q=is%3Aissue+is%3Aactive",
            }
            
            send_emails(
                emails=email_list["emails"],
                sender_email=email,
                smtp_server=server,
                port=port,
                password=password,
                subject= website_title + "の最新文章：" + article["title"],
                body="文章链接：" + article["link"] + "\n" + "文章内容：" + article["summary"] + "\n" + "发布时间：" + article["published"],
                template_path=email_template,
                template_data=template_data,
                use_tls=use_tls
            )
