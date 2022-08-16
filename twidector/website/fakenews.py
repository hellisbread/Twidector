fakenews.py
import pandas as pd
import sshtunnel
import logging
from datetime import datetime 
from sshtunnel import SSHTunnelForwarder
import pymysql
import pymysql.cursors
from bs4 import BeautifulSoup
import urllib.request,sys,time
import requests
from dateutil.parser import parse
import contractions
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score
import tweepy
from nltk.stem.porter import *
import numpy as np

#establish connection to database

server_ssh_host= "ssh.pythonanywhere.com"
server_ssh_user= "twidector"
server_ssh_password= "SIMfypTopic18"

server_host= "twidector.mysql.pythonanywhere-services.com"
server_port= 3306
server_user= "twidector"
server_password= "FYP22S205"
server_db= "twidector$default"

email_port = 465
email_smtp_server = "smtp.gmail.com"
email_email = "twidector@gmail.com"
email_password = "hvxxdoxsxrtsinbu"

serverhost='db-mysql-sgp1-59801-do-user-11772463-0.b.db.ondigitalocean.com'
serverport=25060
serveruser='doadmin'
serverpassword='AVNS_8sOuFo_0JsSYDZDq3bL'
serverdb='defaultdb'

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

def insertRecords_DB():
    open_connect()

#Twitter API Tokens
api_key = 'WkC302nPjoYVv1Jqo0iqylYuC'
api_key_secret = 'DVl2UrqBPAo3MORzt97ijYY3xkpDjjh4wNTZ4exRPJL5edLlrz'
access_token = '1538432651266121728-jhXmfUQ0B4Fr5PAxHBtPTYKkznVLJQ'
access_token_secret =  'Tt3995pRdxAFD1zOh9AIziL687tdqarU2139MbxjhWzVK'

auth = tweepy.OAuthHandler(api_key,api_key_secret)
auth.set_access_token(access_token,access_token_secret)

api = tweepy.API(auth)

#establish connection and set bearer token
client = tweepy.Client(bearer_token='AAAAAAAAAAAAAAAAAAAAAGe0dwEAAAAAmy8oW7Nxwgg41b9ss1DPSPdJmIY%3DNWjl9LF6yvvbCDBHBFYeFmYk3FUI3MlSHXFsGWST6RHyHyzBD0')

#retrieve the latest date in fake_news_score table
def DB_LatestDate():
    open_connect()
    sql = "SELECT date_time FROM fake_news_score ORDER BY date_time DESC"
    with connection.cursor() as cursor:
        cursor.execute(sql)
        date = cursor.fetchmany(size=1)
        for a_date in date:
            fetch_date = a_date['date_time']
        close_connect()
        return fetch_date

#retrieve latest news    
def webscrape_data():
    
    list_of_date = []
    frame = []
    #fetch the latest date in stored db
    fetch_date = DB_LatestDate()
    
    url = "https://www.politifact.com/factchecks/list/?page=" + str(1)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('li',attrs={'class':'o-listicle__item'})
    
    for j in links:
        
        Date = j.find('div',attrs={'class':'m-statement__body'}).find('footer').text
        Date = parse(Date , fuzzy=True)
        label = j.find('div', attrs ={'class':'m-statement__content'}).find('img',attrs={'class':'c-image__original'}).get('alt').strip()
        
        #retrieve updated news and only if news that are either TRUE or FALSE
        if (Date > fetch_date and (label == 'true' or label == 'false')):
            Statement = j.find("div", attrs = {'class' : 'm-statement__quote'}).text.strip()
            frame.append((Statement, label, Date))
    
    data = pd.DataFrame(frame, columns=['Statement', 'Label', 'Date'])
    
    return data

#reading the fakenewsDetection.csv
df = pd.read_csv("fakeNewsDetection.csv")
df = df.dropna()
new_df = df[(df["Label"] == "TRUE") | (df["Label"] == "FALSE")]
count = 0

def cleanStatements(tweet):
    
    stopwords = nltk.corpus.stopwords.words("english")
    #extending the stopwords to include other words used in twitter such as retweet(rt) etc.
    other_exclusions = ["#ff", "ff", "rt"]
    stopwords.extend(other_exclusions)
    lem = WordNetLemmatizer()
    stemmer = PorterStemmer()
    
    # removal of extra spaces
    regex_pat = re.compile(r'\s+')
    tweet_space = tweet.str.replace(regex_pat, ' ')

    # removal of @name[mention]
    regex_pat = re.compile(r'@[\w\-]+')
    tweet_name = tweet_space.str.replace(regex_pat, '')

    # removal of links[https://abc.com]
    giant_url_regex =  re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|'
            '[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    tweets = tweet_name.str.replace(giant_url_regex, '')
    
    # removal of punctuations and numbers
    punc_remove = tweets.str.replace("[^a-zA-Z]", " ")
    # remove whitespace with a single space
    newtweet=punc_remove.str.replace(r'\s+', ' ')
    # remove leading and trailing whitespace
    newtweet=newtweet.str.replace(r'^\s+|\s+?$','')
    # replace normal numbers with numbr
    newtweet=newtweet.str.replace(r'\d+(\.\d+)?','numbr')
    # removal of capitalization
    tweet_lower = newtweet.str.lower()
    
    # tokenizing
    tokenized_tweet = tweet_lower.apply(lambda x: x.split())
    
    # removal of stopwords
    tokenized_tweet=  tokenized_tweet.apply(lambda x: [item for item in x if item not in stopwords])
    
    # lemmatize tweets
    tokenized_tweet = tokenized_tweet.apply(lambda x: [lem.lemmatize(i , pos="v") for i in x]) 
    
    for i in range(len(tokenized_tweet)):
        tokenized_tweet[i] = ' '.join(tokenized_tweet[i])
        #cleaned_tweet = tokenized_tweet

    return tokenized_tweet

# insert updated data into our model
def insert_webScrape_Data():
    
    #retrieve dataframe after webscraping
    data = webscrape_data()
    
    #insert the data into fake_news_score database table 
    if not data.empty:
        
        #clean the statements
        clean_statements = cleanStatements(data["Statement"])
        data['Clean_Statements'] = clean_statements

        open_connect()
        
        for i, d in data.iterrows():
            
            score = 0
            if (d['label'] == "false"):
                score = 1
            elif (d['label'] == "true"):
                score = 0
                
            statement = d['Clean_Statements']
            date = d['Date']
            
            sql = "INSERT INTO `fake_news_score`(`fake_news_text`, `fake_news_score`, `date_time`) VALUES(%s, %s, %s)"
            with connection.cursor() as cursor:
                insert_list = [statement, int(score) , date]
                cursor.execute(sql, tuple(insert_list))
                connection.commit()

        close_connect()


#retrieve the trainData
def retrieve_trainData():
    open_connect()
    try:
        sql = "SELECT * FROM fake_news_score"
        data = pd.read_sql(sql , connection)
        close_connect()
        return data
    except:
        close_connect()
        return "Retreieve train data unsuccessful"

#train the fake news prediction model
def train_FN_Model():
    
    global FN_vectorizer
    global linear_model
    
    data = retrieve_trainData()
    
    #train test and split the data
    x = data['fake_news_text']
    y = data['fake_news_score']
    
    x_train, x_test, y_train, y_test = train_test_split(x, y, stratify = y, test_size=0.2)
    
    #fit into bag of words and transform data into a matrix
    FN_vectorizer = TfidfVectorizer(ngram_range = (1 , 3), max_features = 2000)
    FN_vectorizer.fit(list(x_train) + list(x_test))
    
    x_train_vec = FN_vectorizer.transform(x_train)
    x_test_vec = FN_vectorizer.transform(x_test)
    
    #fit the matrix data into the SVC model
    linear_model = LinearSVC(C = 0.05)
    linear_model.fit(x_train_vec, y_train)
    prediction = linear_model.predict(x_test_vec)
    score = accuracy_score(y_test, prediction) * 100
    return score


    #retrieve tweets from database
def retrieveTweet_DB(userID):
    
    open_connect()
    sql = "SELECT * FROM tweet WHERE screen_name = %s"
    
    with connection.cursor() as cursor:
        cursor.execute(sql, userID)
        result = cursor.fetchall()
        close_connect()  
        return result

#insert tweet into DB
def insert_into_DB_FN(df):
    
    open_connect()
    
    for index, row in df.iterrows():
        
        tweet_id = row['Tweet_ID']
        screen_name = row['Screen_Name']
        tweet_date = row['Date_Time']
        tweet_text = row['Tweets']
        predicted_fake_score = row['FN_Prediction']
        retweet = row['Retweet']
        
        sql = "INSERT INTO `tweet`(`tweet_id`, `screen_name`, `tweet_date`, `tweet_text`,`predicted_fake_score`, `flagged`, `offensive_count`, `hateful_count`, `neutral_count`, `fake_news_count`, `admin_interjection`, `retweet`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        with connection.cursor() as cursor:
            insert_list = [tweet_id, screen_name, tweet_date, tweet_text, predicted_fake_score, 0, 0, 0, 0, 0, 0, retweet]
            cursor.execute(sql, tuple(insert_list))
            connection.commit()
            
    close_connect()

#retrieve the tweets from Twitter   
def retrieveTweets_Twitter(userID):
    
    list_of_tweet_info = []
    results = api.user_timeline(screen_name = userID, count=100)
    
    for result in results:

        info = []
        
        x = re.search("^RT", result.text)
        if x:
            retweet = 'true'
        else:
            retweet = 'false'
            
        info.append(result.id)
        info.append(userID)
        info.append(result.text)
        info.append(result.created_at)
        info.append(retweet)
        list_of_tweet_info.append(info)
    
    data = pd.DataFrame(list_of_tweet_info, columns=['Tweet_ID', 'Screen_Name', 'Tweets', 'Date_Time', 'Retweet'])
    
    return data


#predict tweet if its fake news
def predictFN(df):
    
    screen_name_list = ["cnnbrk", "CNN", "nytimes", "BBCBreaking", "BBCWorld", "TheEconomist", "Reuters",
                       "WSJ", "washingtonpost", "TIME", "ABC", "ndtv", "AP", "ChannelNewsAsia"]
    
    clean_tweets = df['Clean_Tweets']
    screen_name = df['Screen_Name']
    
    if screen_name[0] in screen_name_list:
        matrix = FN_vectorizer.transform(clean_tweets)
        prediction = linear_model.predict(matrix)
        df['FN_Prediction'] = prediction
    
    else:
        prediction = []
        for row in df.iterrows():
            prediction.append(2)
        df['FN_Prediction'] = prediction
        
    return df

def score_the_user(TwitterHandle):
    
    score  = 0
    #checks if the user is verified
    user = client.get_user(username = TwitterHandle, user_fields = 'verified')
    if user.data.verified == True:
        score += 1
    return score


# #display tweets of a user
def display_tweets(TwitterHandle):
    try:
        result = retrieveTweet_DB(TwitterHandle)
    except:
        return "There is no such user registered with Twitter"
    
    #user has not been searched before
    if not result:
        
        df = retrieveTweets_Twitter(TwitterHandle)
        
        #clean the tweets
        clean_tweets = cleanStatements(df["Tweets"])
        df['Clean_Tweets'] = clean_tweets
        
        #predict the clean tweets
        df = predictFN(df)
        
        #insert the tweets into db
        insert_into_DB_FN(df)
    
    #user has been searched before
    else:

#insert the webscrape data
insert_webScrape_Data()

#retrieve the data from db and train the model
train_FN_Model()

#query and display the tweets
display_tweets('CNN')

#score the user profile
score_the_user("CNN")

