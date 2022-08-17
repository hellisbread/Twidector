from fileinput import close
from mysql.connector.errors import IntegrityError
import pymysql.cursors
import hashlib
import os
import secrets
import email.utils
import requests
from itsdangerous import URLSafeTimedSerializer
#from flask import redirect, render_template, url_for
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

import sshtunnel
import logging
from sshtunnel import SSHTunnelForwarder
#import config

from website.config import *

salt = os.urandom(32)
ts = URLSafeTimedSerializer(salt)

sshtunnel.SSH_TIMEOUT = 120.0
sshtunnel.TUNNEL_TIMEOUT = 120.0

def open_ssh_tunnel():
    
    global tunnel
    
    tunnel = SSHTunnelForwarder(
        (server_ssh_host),
        ssh_username = server_user,
        ssh_password = server_ssh_password,
        remote_bind_address = ('twidector.mysql.pythonanywhere-services.com', 3306)
    )
    
    tunnel.start()

def close_ssh_tunnel():
    tunnel.close

def open_server():

    global connection

    connection = pymysql.connect(
        user = server_user,
        password = server_password,
        host ='127.0.0.1', #sus
        port =tunnel.local_bind_port,
        db = server_db,
        charset = "utf8",
        cursorclass = pymysql.cursors.DictCursor
    )
    
def close_server():
    connection.close()

def open_connect():
    open_ssh_tunnel()
    open_server()
    
def close_connect():
    close_server()
    close_ssh_tunnel()

def generate_token(email):
    
    token = ts.dumps(email, salt="salt")
    
    return token

def send_email(recipient, subject, body):
    port = email_port
    smtp_server = email_smtp_server
    sender_email = email_email
    password = email_password
    
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
    body = ""
    body += html
    
    send_email(email, subject, body)

def send_reset_password_email(email, html):
    subject = "Twidector account password reset"
    body = ""
    body += html
    
    send_email(email, subject, body)

def confirm_email(token):
    try:
        email = ts.loads(token, salt="salt", max_age=86400)
    except:
        return "Error404"

    #user = User.query.filter_by(email=email).first_or_404()

    #user.email_confirmed = True

    with connection.cursor() as cursor:     

        sqlcommand = "UPDATE `UserInfo` SET `confirmed` WHERE (%s)"
        cursor.execute(sqlcommand, (1))
        connection.commit()

    return True

def salting():
    salt = os.urandom(32)

    return salt

def encrypt(text):
    salt = salting()
    encrypted = hashlib.pbkdf2_hmac('sha256', text.encode("utf-8"), salt, 100000)

    salt_and_encrypted = { "salt" : salt,
                            "encrypted" : encrypted}

    return salt_and_encrypted

def retrieve_user_by_username(username):
    
    open_connect()

    with connection.cursor() as cursor:

        sqlcommand = "SELECT `username`, `activated` FROM `UserInfo` WHERE `username` = %s"

        try:

            cursor.execute(sqlcommand, (username))

            close_connect()
            return True

        except pymysql.IntegrityError:
            close_connect()
            return False


#def retrieve_salt_by_email(email):
    
    open_connect()

    with connection.cursor() as cursor:

        sqlcommand = "SELECT `salt` FROM `UserInfo` WHERE `email` = %s"

        try:

            cursor.execute(sqlcommand, (email))

            close_connect()
            return True

        except pymysql.IntegrityError:
            close_connect()
            return False

def reset_user_password(email, password):
    
    open_connect()

    with connection.cursor() as cursor:
        try:
            sqlcommand = "SELECT `salt` FROM `UserInfo` WHERE `email` = %s"
            cursor.execute(sqlcommand, (email))

            result = cursor.fetchone()

            salt = result["salt"]

            newkey = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

            sqlcommand = "UPDATE `UserInfo` SET `key` = %s WHERE `email` = %s"
            cursor.execute(sqlcommand, (newkey, email))
            connection.commit()

            close_connect()
            return True

        except pymysql.IntegrityError:
            close_connect()
            return False



def recover_username(email):

    open_connect

    with connection.cursor() as cursor:
        
        sqlcommand = "SELECT `username` FROM `UserInfo` WHERE `email` = %s"
        
        try:
            cursor.execute(sqlcommand, (email))
            result = cursor.fetchone()

            close_connect()
            return ("Your username has been sent to the email submitted")
        
        except:
            close_connect()
            return ("Invalid")

    
        
#send to email

def recover_password(username, email):

    open_connect()

    with connection.cursor() as cursor:
        
        sqlcommand = "SELECT `username`, `email` FROM `UserInfo` WHERE `username` = %s AND `email` = %s"
        
        try:
            cursor.execute(sqlcommand, (username, email)) 
            result = cursor.fetchone()
        
            if (username == result["username"] and
                email == result["email"]):
                return ("A reset link has been sent to the email submitted. Please continue reset instructions from there.")
            
            else:
                close_connect()
                return ("Invalid")
        
        except:
            close_connect()
            return ("Invalid")

    

#will send an email to user
def change_password(username, password):

    open_connect()

    with connection.cursor() as cursor:

        encrypt_dict = encrypt(password)

        sqlcommand = "UPDATE `UserInfo` SET `salt` = %s ,`key` = %s WHERE `username` = %s"
        cursor.execute(sqlcommand, (encrypt_dict["salt"],encrypt_dict["encrypted"],username))
        
        connection.commit()
        return True
    
    close_connect()

#willsend an email to user
#requires password to change email
def change_email(username, email, password):

    open_connect()

    with connection.cursor() as cursor:

        encrypt_dict = encrypt(password)

        sqlcommand = "UPDATE `UserInfo` SET `email` = %s WHERE `username` = %s"
        cursor.execute(sqlcommand, (email,username))
        
        connection.commit()
        print("Email changed success")

    close_connect()
        
#change to send by email method eventually
#dont have to validate email here, dont let attackers know what usernames/emails exist

def delete_account(username):
    open_connect()

    with connection.cursor() as cursor:
        sqlcommand = "DELETE FROM `UserInfo` WHERE `username` = %s"
        cursor.execute(sqlcommand, (username))
        
        connection.commit()
        print("Deletion success")

    close_connect()

# Delete button -> Are you sure you want to delete -> Yes -> delete_account
def tweet_score(tweet_id, admin_hate_result):
    open_connect()

    with connection.cursor() as cursor:
        sqlcommand = "UPDATE `tweet` SET `admin_interjection`=1, `admin_hate_result`=%s,`fitted_hate`=0 WHERE `tweet_id`=%s"
        cursor.execute(sqlcommand, (admin_hate_result, tweet_id))
        connection.commit()
        close_connect()
