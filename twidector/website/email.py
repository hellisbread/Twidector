import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config

def send_email(recipient, subject, body):
    port = config.emailport
    smtp_server = config.emailsmtp_server
    sender_email = config.emailemail
    password = config.emailpassword
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    
    server = smtplib.SMTP_SSL(smtp_server, port)
    
    server.login(sender_email, password)
    server.sendmail(sender_email, recipient, msg.as_string())
    server.quit()


send_email("twidector@gmail.com", "My Test Email", "Hello from Python!")