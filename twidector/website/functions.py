from mysql.connector.errors import IntegrityError
import pymysql.cursors
import hashlib
import os
import secrets
import email.utils
import requests
from itsdangerous import URLSafeTimedSerializer
from flask import redirect, render_template, url_for
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

#import config

from website.config import *

connection = pymysql.connect(host = serverhost,
                             port = serverport,
                             user = serveruser,
                             password = serverpassword,
                             db = serverdb,
                             charset = "utf8",
                             cursorclass = pymysql.cursors.DictCursor)

salt = os.urandom(32)
ts = URLSafeTimedSerializer(salt)

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
    body = "Welcome to Twidector! You are just one click away from the completion of your registration. Please click the following link to complete your registration:"
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

    return redirect(url_for('signin'))

def validate_login(username, password):
    with connection.cursor() as cursor:
        
        try:
        
            sqlcommand = "SELECT `salt`, `key`, `confirmed` FROM `UserInfo` WHERE `username` = %s"
            cursor.execute(sqlcommand, (username))

            result = cursor.fetchone()

            salt = result["salt"]
            
            key = result["key"]
            
            
            currentkey = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

            if ((secrets.compare_digest(currentkey,key) == True) and (result["confirmed"]) == True):
                return ("Valid")
            
            elif ((secrets.compare_digest(currentkey,key) == True) and (result["confirmed"]) == False):
                return ("Account not confirmed")
            
            else:
                return ("Invalid")
            
        except:
            return ("Invalid")

def register_user(username, password, user_type, email):
    
    with connection.cursor() as cursor:

        salt = os.urandom(32)

        key = hashlib.pbkdf2_hmac('sha256', password.encode("utf-8"), salt, 100000)

        sqlcommand = "INSERT INTO `UserInfo` (`username`, `salt`, `key`, `user_type`, `email`, `confirmed`) VALUES (%s, %s, %s, %s, %s, %s)"

        try:

            cursor.execute(sqlcommand, (username, salt, key, user_type, email, 0))
            connection.commit()

            token = generate_token(email)
            confirm_url = url_for("confirm_email", token=token, _external=True)
            
            html = render_template("activate.html", confirm_url=confirm_url)
            send_registration_email(email, html)
        
            return redirect(url_for("index"))

        except pymysql.IntegrityError:
          return ("Username already exists")


#companyname
#salting hashing here
#send email for verification here


#def register_twitter_user(username, password, usertype, email, twitterusername):
          
    is_valid = validate_email(email)
    
    if (is_valid == True):
    
        with connection.cursor() as cursor:

            salt = os.urandom(32)
            
            key = hashlib.pbkdf2_hmac('sha256', password.encode("utf-8"), salt, 100000)
            
            sqlcommand = "INSERT INTO `UserInfo` (`username`, `salt`, `key`, `usertype`, `email`, `twitterusername`) VALUES (%s, %s, %s, %s, %s, %s)"
            
            try:
                cursor.execute(sqlcommand, (username, salt, key, usertype, email, twitterusername))
                connection.commit()
                return True

            except pymysql.IntegrityError:
              return False
        
    else:
        return True


def recover_username(email):
    with connection.cursor() as cursor:
        
        sqlcommand = "SELECT `username` FROM `UserInfo` WHERE `email` = %s"
        
        try:
            cursor.execute(sqlcommand, (email))
            result = cursor.fetchone()

            return ("Your username has been sent to the email submitted")
        
        except:
            return ("Invalid")
        
#send to email

def recover_password(username, email):
    with connection.cursor() as cursor:
        
        sqlcommand = "SELECT `username`, `email` FROM `UserInfo` WHERE `username` = %s AND `email` = %s"
        
        try:
            cursor.execute(sqlcommand, (username, email)) 
            result = cursor.fetchone()
        
            if (username == result["username"] and
                email == result["email"]):
                return ("A reset link has been sent to the email submitted. Please continue reset instructions from there.")
            
            else:
                return ("Invalid")
        
        except:
            return ("Invalid")
        
#change to send by email method eventually
#dont have to validate email here, dont let attackers know what usernames/emails exist


def whitelist_user(username, targetUser):

    with connection.cursor() as cursor:

        sqlcommand = "INSERT INTO `WhitelistTable` (`username`, `whitelisted`) VALUES (%s, %s)"

        try:
            cursor.execute(sqlcommand, (username, targetUser))
            connection.commit()

        except pymysql.IntegrityError:
          return ("Already whitelisted")

def retrieve_whitelist(username):
    with connection.cursor() as cursor:
        sqlcommand = "SELECT `whitelisted` FROM `WhitelistTable` WHERE `username` = %s"
        cursor.execute(sqlcommand, (username))
        result = cursor.fetchall()
        for item in result:
            print(item["whitelisted"])

def blacklist_user(username, targetUser):

    with connection.cursor() as cursor:

        sqlcommand = "INSERT INTO `BlacklistTable` (`username`, `blacklisted`) VALUES (%s, %s)"

        try:
            cursor.execute(sqlcommand, (username, targetUser))
            connection.commit()

        except pymysql.IntegrityError:
          return ("Already blacklisted")

def retrieve_blacklist(username):
    with connection.cursor() as cursor:
        sqlcommand = "SELECT `blacklisted` FROM `BlacklistTable` WHERE `username` = %s"
        cursor.execute(sqlcommand, (username))
        result = cursor.fetchall()
        for item in result:
            print(item["blacklisted"])


#Twitter Function not DB
def block_user(username, targetUser):

    with connection.cursor() as cursor:

        sqlcommand = "INSERT INTO `BlockTable` (`username`, `blocked`) VALUES (%s, %s)"

        try:
            cursor.execute(sqlcommand, (username, targetUser))
            connection.commit()

        except pymysql.IntegrityError:
          return ("Already blocked")

#Twitter Function not DB
def retrieve_blocked(username):
    with connection.cursor() as cursor:
        sqlcommand = "SELECT `blocked` FROM `BlockTable` WHERE `username` = %s"
        cursor.execute(sqlcommand, (username))
        result = cursor.fetchall()
        for item in result:
            print(item["blocked"])

def delete_account(username):
    with connection.cursor() as cursor:
        sqlcommand = "DELETE FROM `UserInfo` WHERE `username` = %s"
        cursor.execute(sqlcommand, (username))
        
        connection.commit()
        print("Deletion success")

# Delete button -> Are you sure you want to delete -> Yes -> delete_account


#unfollow twitter user - This is a twitter function!
#on click unfollow button(should only appear after followed)
def unfollow_user(username, target_user):

    with connection.cursor() as cursor:

        sqlcommand = "DELETE FROM `FollowedUsers` WHERE `username` = %s AND `followeduser` = %s"

        cursor.execute(sqlcommand, (username, target_user))
        connection.commit()

        return('you have unfollowed the user:' + target_user)