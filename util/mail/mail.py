import os.path
import smtplib
from email import message
from email.utils import formatdate
from config import conf

def send(email, subject, text):
    s = smtplib.SMTP_SSL(conf.smtp.get('host'), conf.smtp.get('port'))
    s.login(conf.smtp.get('user'), conf.smtp.get('pass'))
    msg = message.EmailMessage()
    msg.set_content(text)
    msg['Subject'] = subject
    msg['From'] = conf.smtp.get('address')
    msg['Date'] = formatdate()
    msg['To'] = email
    s.send_message(msg)
    s.quit()

def send_template(email, subject, template_name, *args, **kwargs):
    with open(os.path.join(os.path.dirname(__file__), f'{template_name}.html'),'r', encoding='utf-8') as f:
        text = f.read()
        text = text.format(**kwargs)
    send(email, subject, text)