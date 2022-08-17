import os

server_ssh_host= os.getenv('SERVER_SSH_HOST')
server_ssh_user= os.getenv('SERVER_SSH_USER')
server_ssh_password= os.getenv('SERVER_SSH_PASSWORD')

server_host= os.getenv('PROD_SQL_HOST')
server_port= 3306
server_user= os.getenv('PROD_SQL_USER')
server_password= os.getenv('PROD_SQL_PASSWORD')
server_db= os.getenv('PROD_SQL_NAME')

email_port = 465
email_smtp_server = os.getenv('EMAIL_HOST')
email_email = os.getenv('EMAIL_HOST_USER')
email_password = os.getenv('EMAIL_HOST_PASSWORD')

# serverhost='db-mysql-sgp1-59801-do-user-11772463-0.b.db.ondigitalocean.com'
# serverport=25060
# serveruser='doadmin'
# serverpassword='AVNS_8sOuFo_0JsSYDZDq3bL'
# serverdb='defaultdb'

twitter_key = os.getenv('TWITTER_API_KEY')
twitter_key_secret = os.getenv('TWITTER_API_SECRET')
twitter_access = os.getenv('TWITTER_ACCESS_TOKEN')
twitter_access_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')