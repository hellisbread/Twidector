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

def block_user(username, targetUser):

    with connection.cursor() as cursor:

        sqlcommand = "INSERT INTO `BlockTable` (`username`, `blocked`) VALUES (%s, %s)"

        try:
            cursor.execute(sqlcommand, (username, targetUser))
            connection.commit()

        except pymysql.IntegrityError:
          return ("Already blocked")

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


#unfollow twitter user
#on click unfollow button(should only appear after followed)
def unfollow_user(username, target_user):

    with connection.cursor() as cursor:

        sqlcommand = "DELETE FROM `FollowedUsers` WHERE `username` = %s AND `followeduser` = %s"

        cursor.execute(sqlcommand, (username, target_user))
        connection.commit()

        return('you have unfollowed the user:' + target_user)