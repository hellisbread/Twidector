import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config
import functions

def send_email(recipient, subject, body):
    port = config.email_port
    smtp_server = config.email_smtp_server
    sender_email = config.email_email
    password = config.email_password
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = subject
    body = MIMEText(body)
    msg.attach(body)

    server = smtplib.SMTP_SSL(smtp_server, port)
    
    server.login(sender_email, password)
    server.sendmail(sender_email, recipient, msg.as_string())
    server.quit()

def send_registration_email(email, html):
    subject = "Twidector account registration"
    body = "Welcome to Twidector! You are just one click away from the completion of your registration. Please click the following link to complete your registration:"
    body += html
    
    send_email(email, subject, body)

def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash("Invalid", "danger")
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash("Account already confirmed.", "success")
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("Account has been confirmed", "success")
    return redirect(url_for('main.home'))