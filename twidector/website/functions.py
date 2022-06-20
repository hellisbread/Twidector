from validate_email import validate_email
from mysql.connector.errors import IntegrityError
import pymysql.cursors
import hashlib
import os
import secrets
import email.utils
import requests
from flask import Flask, url_for

import config
import mail_system

connection = pymysql.connect(host = config.server_host,
                             port = config.server_port,
                             user = config.server_user,
                             password = config.server_password,
                             db = config.server_db,
                             charset = "utf8",
                             cursorclass = pymysql.cursors.DictCursor)


from website.config import *

connection = pymysql.connect(host = serverhost,
                             port = serverport,
                             user = serveruser,
                             password = serverpassword,
                             db = serverdb,
                             charset = "utf8",
                             cursorclass = pymysql.cursors.DictCursor)

def generate_token(email):
    salt = os.urandom(32)
    token = hashlib.pbkdf2_hmac('sha256', email.encode("utf-8"), salt, 100000)
    
    return token

def confirm_token(token):
    try:
        email = serializer.loads(
            token,
            max_age=60
        )
    except:
        return False
    return email

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
            
            return ("An email has been sent. Follow the instructions to complete registration.")

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


