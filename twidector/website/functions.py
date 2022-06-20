from validate_email import validate_email
from mysql.connector.errors import IntegrityError
import pymysql.cursors
import hashlib
import os
import secrets


from website.config import *

connection = pymysql.connect(host = serverhost,
                             port = serverport,
                             user = serveruser,
                             password = serverpassword,
                             db = serverdb,
                             charset = "utf8",
                             cursorclass = pymysql.cursors.DictCursor)


def validateLogin(username, password):
    with connection.cursor() as cursor:
        
        try:
        
            sqlcommand = "SELECT `salt`, `key` FROM `UserInfo` WHERE `username` = %s"
            cursor.execute(sqlcommand, (username))

            result = cursor.fetchone()

            salt = result["salt"]
            
            key = result["key"]
            
            currentkey = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

            if (secrets.compare_digest(currentkey,key) == True):
                return True
            else:
                return False
            
        except:
            return False

def registerUser(username, password, usertype, email):
          
    is_valid = validate_email(email)
    
    if (is_valid == True):
    
        with connection.cursor() as cursor:

            salt = os.urandom(32)
            
            key = hashlib.pbkdf2_hmac('sha256', password.encode("utf-8"), salt, 100000)
            
            sqlcommand = "INSERT INTO `UserInfo` (`username`, `salt`, `key`, `usertype`, `email`) VALUES (%s, %s, %s, %s, %s)"
            
            try:
                cursor.execute(sqlcommand, (username, salt, key, usertype, email))
                connection.commit()
                return True

            except pymysql.IntegrityError:
              return False
        
    else:
        return False

#companyname
#salting hashing here
#send email for verification here


#def registerTwitterUser(username, password, usertype, email, twitterusername):
          
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


