from validate_email import validate_email
#from mysql.connector.errors import IntegrityError
from django.db import IntegrityError
from cryptography.fernet import Fernet
import pymysql.cursors

connection = pymysql.connect(host='db-mysql-sgp1-59801-do-user-11772463-0.b.db.ondigitalocean.com',
                             port=25060,
                             user='doadmin',
                             password='AVNS_8sOuFo_0JsSYDZDq3bL',
                             db='defaultdb',
                             cursorclass=pymysql.cursors.DictCursor)


def validateLogin(username, password):
    with connection.cursor() as cursor:
        
        try:
        
            sqlcommand = "SELECT `key`, `salt` FROM `UserInfo` WHERE `username` = %s"
            cursor.execute(sqlcommand, (username))

            result = cursor.fetchone()

            #bytepassword = password.encode("utf-8")

            cipher_suite = Fernet(result["key"])

            bytepassword = result["salt"].encode("utf-8")

            unciphered = (cipher_suite.decrypt(bytepassword))
            #print(unciphered)

            plain = bytes(unciphered).decode("utf-8")
            #print("plain :" + plain)

            if (password == plain):
                return True
            else:
                return False
            
        except:
            return False


def registerUser(username, password, usertype, email, twitterusername):
          
    is_valid = validate_email(email)
    
    if (is_valid == True):
    
        with connection.cursor() as cursor:

            key = Fernet.generate_key()
            cipher_suite = Fernet(key)
            
            bytepassword = password.encode("utf-8")
            
            ciphered = cipher_suite.encrypt(bytepassword)
            sqlcommand = "INSERT INTO `UserInfo` (`username`, `key`, `salt`, `usertype`, `email`, `twitterusername`) VALUES (%s, %s, %s, %s, %s, %s)"
            
            try:
                cursor.execute(sqlcommand, (username, key, ciphered, usertype, email, twitterusername))
                connection.commit()
                return True

            except pymysql.IntegrityError:
                return False
        
    else:
        return ("Invalid email")

#companyname
#salting hashing here
#send email for verification here