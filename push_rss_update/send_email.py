import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import os
import time

# 配置日志记录
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
    发送电子邮件给多个目标邮箱，并记录详细日志。
    """
    logging.debug(f'准备发送邮件，发件人: {sender_email}，收件人: {", ".join(target_emails)}，主题: {subject}')
    
    # 创建 MIME 对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(target_emails)
    msg['Subject'] = subject

    if template_path and template_data:
        env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
        template = env.get_template(os.path.basename(template_path))
        html_content = template.render(template_data)
        msg.attach(MIMEText(html_content, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))

    # 连接到 SMTP 服务器并发送邮件
    for attempt in range(retries):
        try:
            logging.debug(f'尝试连接到 SMTP 服务器: {smtp_server}，端口: {port}')
            with smtplib.SMTP(smtp_server, port) as server:
                if use_tls:
                    logging.debug('启动 TLS 加密')
                    server.starttls()
                logging.debug('登录到 SMTP 服务器')
                server.login(sender_email, password)
                logging.debug('发送邮件')
                server.sendmail(sender_email, target_emails, msg.as_string())
                logging.info(f'邮件已成功发送到: {", ".join(target_emails)}')
                return  # 成功发送后退出
        except smtplib.SMTPException as e:
            logging.error(f'邮件发送失败，目标地址: {", ".join(target_emails)}，错误信息: {e}')
            if attempt < retries - 1:
                logging.debug(f'等待 {delay} 秒后重试...')
                time.sleep(delay)  # 等待后重试
            else:
                logging.error(f'所有重试均失败，未能发送邮件到: {", ".join(target_emails)}')

def send_emails(target_emails, sender_email, smtp_server, port, password, subject, body, template_path=None, template_data=None, use_tls=True):
    """
    向多个邮箱发送一封邮件。
    """
    logging.info(f'正在发送邮件到: {", ".join(target_emails)}，邮件主题: {subject}')
    email_sender(target_emails, sender_email, smtp_server, port, password, subject, body, template_path, template_data, use_tls)

