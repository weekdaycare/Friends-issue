import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import os
import time

def email_sender(
    target_emails,
    sender_email, 
    smtp_server, 
    port, 
    password, 
    subject, 
    body,
    template_path=None,
    template_data=None,
    use_tls=True,
    retries=3,
    delay=3,
    ):
    """
    发送电子邮件给多个目标邮箱。

    参数：
    target_emails (list): 目标邮箱地址列表。
    sender_email (str): 发信邮箱地址。
    smtp_server (str): SMTP 服务地址。
    port (int): SMTP 服务端口。
    password (str): SMTP 服务密码。
    subject (str): 邮件主题。
    body (str): 邮件内容。
    template_path (str): HTML 模板文件路径。默认为 None。
    template_data (dict): 渲染模板的数据。默认为 None。
    use_tls (bool): 是否使用 TLS 加密。默认为 True。
    retries (int): 邮件发送失败时的重试次数，默认为 3。
    delay (int): 重试之间的延迟时间（秒），默认为 3。
    """
    # 创建 MIME 对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(target_emails)  # 将多个收件人合并为字符串
    msg['Subject'] = subject

    if template_path and template_data:
        # 使用 Jinja2 渲染 HTML 模板
        env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
        template = env.get_template(os.path.basename(template_path))
        html_content = template.render(template_data)
        msg.attach(MIMEText(html_content, 'html'))
    else:
        # 添加纯文本邮件内容
        msg.attach(MIMEText(body, 'plain'))

    # 连接到 SMTP 服务器并发送邮件
    for attempt in range(retries):
        try:
            with smtplib.SMTP(smtp_server, port) as server:
                server.set_debuglevel(1)
                server.ehlo()
                if use_tls:
                    server.starttls()  # 启动安全模式
                server.login(sender_email, password)
                server.sendmail(sender_email, target_emails, msg.as_string())
                logging.info(f'邮件已成功发送到 {", ".join(target_emails)}')
                break  # 成功发送后退出
        except smtplib.SMTPException as e:
            logging.error(f'邮件发送失败，目标地址: {", ".join(target_emails)}，执行第 {attempt + 1} 重试')
            if attempt < retries - 1:
                time.sleep(delay)  # 等待后重试
            else:
                logging.error(f'所有重试均失败，未能发送更新邮件，错误信息: {e}')

def send_emails(target_emails, sender_email, smtp_server, port, password, subject, body, template_path=None, template_data=None, use_tls=True):
    """
    向多个邮箱发送一封邮件。

    参数：
    target_emails (list): 包含目标邮箱地址的列表。
    sender_email (str): 发信邮箱地址。
    smtp_server (str): SMTP 服务地址。
    port (int): SMTP 服务端口。
    password (str): SMTP 服务密码。
    subject (str): 邮件主题。
    body (str): 邮件内容。
    template_path (str): HTML 模板文件路径。默认为 None。
    template_data (dict): 渲染模板的数据。默认为 None。
    use_tls (bool): 是否使用 TLS 加密。默认为 True。
    """
    logging.info(f'正在发送邮件到: {", ".join(target_emails)}，邮件主题: {subject}')
    email_sender(target_emails, sender_email, smtp_server, port, password, subject, body, template_path, template_data, use_tls)
