import sklearn as sk
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import pandas as panda
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import *
import pytz
import tweepy
import configparser
import pymysql
import re
import string
import nltk
import math
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics import confusion_matrix
from textstat.textstat import *
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import svm, linear_model
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
#from .maintenance import *
import numpy as np

import warnings

from website.maintenance import load_pickle
warnings.simplefilter(action='ignore', category=FutureWarning)
import sshtunnel
import logging

from datetime import datetime as dt

from sshtunnel import SSHTunnelForwarder

from website.config import *
from website.maintenance import *

import nltk
from nltk.stem import WordNetLemmatizer
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('omw-1.4')
import contractions
from nltk.sentiment.vader import SentimentIntensityAnalyzer as VS

stop_words = nltk.corpus.stopwords.words("english")
    #extending the stopwords to include other words used in twitter such as retweet(rt) etc.
other_exclusions = ["#ff", "ff", "rt"]
stop_words.extend(other_exclusions)
stemmer = PorterStemmer()
vectorizer = CountVectorizer(ngram_range=(1, 4), max_features = 1000)
#vectorizer = HashingVectorizer(n_features=10000,norm=None,alternate_sign=False) 

#model_filename = 'model.sav'



def prepareDF():
    global df
    global vectorizer , x_train, x_test, x_train_vec, y_train , SVM
    #import the dataset
    #filePath = r'C:\Users\User\hateDetection.csv'

    df = pd.read_csv('hateDetection.csv')

    ## 1. Removal of punctuation and capitlization
    ## 2. Tokenizing
    ## 3. Removal of stopwords
    ## 4. Stemming

    #clean_Tweets = preprocess(df["tweet"])
    clean_Tweets = df["tweet"]
    df['clean_tweet'] = clean_Tweets
    #split dataset into training and testing
    y = df["class"].values
    x = df["clean_tweet"].values
    x_train, x_test, y_train, y_test = train_test_split(x, y, stratify = y, test_size=0.2)

    # vectorize tweets for model building
    #vectorizer = CountVectorizer(ngram_range=(1, 4), max_features = 1000)
    #vectorizer = HashingVectorizer(ngram_range=(1, 4))

    # learn a vocabulary dictionary of all tokens in the raw documents
    vectorizer.fit(list(x_train) + list(x_test))

    # transform documents to document-term matrix
    x_train_vec = vectorizer.transform(x_train)
    x_test_vec = vectorizer.transform(x_test)

    SVM = linear_model.SGDClassifier()

    SVM.fit(x_train_vec , y_train)

    y_pred_svm = SVM.predict(x_test_vec)

    #save_pickle(SVM, 'hate_model.sav')
    #save_pickle(vectorizer, 'hate_vectorizer.sav')
    
    #print(accuracy_score(y_test, y_pred_svm) * 100)
    #number of hate, offensive and neutral
    return (accuracy_score(y_test, y_pred_svm) * 100)

def graph_values():
   graph_val =  df["class"].value_counts()
   offensive_num = graph_val[1]
   hate_num = graph_val[0]
   non_hate = graph_val[2]

   return [hate_num, non_hate, offensive_num]

def preprocess(tweet):
    
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
    tokenized_tweet = tweet_lower.apply(lambda x:str(x).split())
    
    # removal of stopwords
    tokenized_tweet=  tokenized_tweet.apply(lambda x: [item for item in x if item not in stop_words])
    
    # stemming of the tweets
    tokenized_tweet = tokenized_tweet.apply(lambda x: [stemmer.stem(i) for i in x]) 
    
    for i in range(len(tokenized_tweet)):
        tokenized_tweet[i] = ' '.join(tokenized_tweet[i])
        tweets_p= tokenized_tweet

    return tweets_p

def cleanStatements(Statements):
    tempArr = []
    #clean the data
    #remove numbers, urls, additional whitespaces and puntuation
    for statement in Statements:
        new_statement = statement.lower()
        new_statement = contractions.fix(new_statement)
        new_statement = re.sub(r'[0-9]+', '', new_statement)
        new_statement = re.sub(r'http\S+', '', new_statement)
        new_statement = re.sub(r'[^\w\s]', '', new_statement)
        new_statement = re.sub(r'\s+', ' ', new_statement)

    #lemmatization and stopwords process
        count_token = 0
        seperator = " "
        stringArr = []
        lem = WordNetLemmatizer()
        tokenization = nltk.word_tokenize(new_statement)
        stop_words = set(stopwords.words('english'))
        for w in tokenization:
            clean_word = lem.lemmatize(w , pos="v")
            if clean_word not in stop_words:
                stringArr.append(clean_word)
            if(count_token == len(tokenization) - 1):
                str = seperator.join(stringArr)
                tempArr.append(str)
                stringArr = []
            count_token += 1
    return tempArr
    


# def retrain(dataframe):
#     #load from file saved model
#     clf = load_model()
    
#     cleaned_tweets = preprocess(dataframe)
#     df['clean_tweet'] = cleaned_tweets
#     y = df["class"].values
#     x = df["clean_tweet"].values
    
#     vectorizer = load_vectorizer('hate_vectorizer.sav')
    
#     vectorizer.fit(list(x))
    
#     x_train_vec = vectorizer.transform(x_train)

#     clf = linear_model.SGDClassifier(max_iter=1000)
    
#     clf.partial_fit(x_train_vec, y)
    
#     #save into file model
#     save_model(clf)
   
def predictHate(tweet):
    
    tempseries = pd.Series(tweet)
    ct = preprocess(tempseries)
    #ct = preprocess(tempseries)
    #print(list(ct))
    # vectorizer.fit(list(ct) + list(x_train) + list(x_test))
    vectorizer = load_pickle('hate_vectorizer.sav')
    m = vectorizer.transform(ct)
    #pred = SVM.predict(m)
    clf = load_pickle('hate_model.sav')
    pred = clf.predict(m)
    return(pred)

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

#estasblish twitter APIv2 connection
#authentication

api_key = twitter_key
api_key_secret = twitter_key_secret

access_token = twitter_access
access_token_secret =  twitter_access_secret

auth = tweepy.OAuthHandler(api_key,api_key_secret)
auth.set_access_token(access_token,access_token_secret)

api = tweepy.API(auth)

#establish connection and set bearer token
client = tweepy.Client(bearer_token=twitter_bearer_token)

def getuserid(twitterhandle):
    users = client.get_users(usernames=[twitterhandle]) 
    for user in users.data:
        return user.id

def getuserUserHandle(twitter_id):
    users = client.get_users(ids=[twitter_id]) 
    for user in users.data:
        return user.username

def getuserIMG(twitterhandle):
    users = client.get_users(ids=[twitterhandle], user_fields=['profile_image_url'])

    for user in users.data:

        imageURL = user.profile_image_url

        #print(imageURL)

        return imageURL.replace("_normal", "")

def getalltweets(userid, limiter):
    tweetarray = []
    tweetidarray = []
    tweetcount = []
    tweetdates = []

    count = 1

    tweets = tweepy.Paginator(client.get_users_tweets,id=userid,tweet_fields=['created_at'],max_results=100,limit=5)

    for tweet in tweets.flatten(limit=limiter): # Total number of tweets to retrieve
        tweetarray.append(tweet.text)
        tweetidarray.append(tweet.id)
        tweetcount.append(count)

        dtime = tweet['created_at']
        new_datetime = dt.strftime(dtime, '%d-%m-%Y')

        tweetdates.append(new_datetime)
        count = count + 1

    temp_df = pd.DataFrame(zip(tweetidarray,tweetarray,tweetcount,tweetdates),columns=['tweetid','tweet','index','date'])
    return(temp_df)

def retrievetweetsviaDatetime(twitter_id,startdate,enddate):
    tweetarray = []                     #tweet text
    tweetidarray = []                   #tweet id
    tweetdate = []                      #tweet creation date
    tweetcount = []

    count = 1

    formatted_start_date = startdate[8:11] + '/' + startdate[5:7] + '/' + startdate[:4]
    formatted_end_date = enddate[8:11] + '/' + enddate[5:7] + '/' + enddate[:4]

    formatted_start_date = dt.strptime(formatted_start_date, '%d/%m/%Y')
    formatted_end_date = dt.strptime(formatted_end_date, '%d/%m/%Y')

    tweets = tweepy.Paginator(client.get_users_tweets,id=twitter_id,max_results=100,limit=5,
                                  tweet_fields = ["created_at"]
                                  #start_time = formatted_start_date,
                                  #end_time = formatted_end_date #veryimpt
                                  )
    for tweet in tweets.flatten(limit = 200):
        dtime = tweet['created_at']

        new_datetime_str = dt.strftime(dtime, '%d-%m-%Y')
        new_datetime = dt.strptime(new_datetime_str, '%d-%m-%Y')
        
        if(formatted_start_date <= new_datetime <= formatted_end_date): 
            tweetarray.append(tweet.text)
            tweetidarray.append(tweet.id)
            tweetcount.append(count)
            tweetdate.append(new_datetime_str)

            count = count + 1

    temp_df = pd.DataFrame(zip(tweetidarray,tweetarray,tweetcount,tweetdate),
                                       columns=['tweetid','tweet','index','date'])
    return temp_df


#should be a global variable, stores the time zone of sg for use later.
TZ_sg = pytz.timezone('Singapore')

#retrieves the tweets from a twitter hangle
def retrieveAndScoreTweets(twitterhandle):
    
    #arrays for different attributes we want to store
    tweetarray = []                     #tweet text
    tweetidarray = []                   #tweet id
    tweetdate = []                      #tweet creation date
    tweetauthorarr = []                 #tweet author(tbh can just set as tweetid given to the api so less things to)  
    tweetRT = []                        #tweet retweet? True/false
    temp_df = []                        #for creation of dataframe of tweets
    
    #get twitter users id
    userID = getuserid(twitterhandle)
    
    #get his tweets
    tweets = client.get_users_tweets(id=userID) 
    
    #checkif user exists and if user exists,
    if checkifuserexists(userID) == 'user exists!':
        print('user already exists in database, checking if they have new tweets!')
        
        now = dt.now(TZ_sg)
        print('connecting to database, checking to see when user was last searched')
        
        #get the date and time of when the last time tweets were retrieved for this user
        #connect to database
        open_connect()
        sqlcommand = 'SELECT `lastretrieved` FROM lastRetrieved WHERE Userid = %s'
        with connection.cursor() as cursor:
            cursor.execute(sqlcommand, (userID))
            last_retrieved_date = cursor.fetchone()
            date_string = dt.strftime(last_retrieved_date['lastretrieved'],"%Y-%m-%d")
            newretrievaldate = dt.strptime(date_string,"%Y-%m-%d")
            
            
        print('user was last updated on: ', date_string)
        print('checking for new tweets after that!' )
        
        #get all new tweets since the last time he's been searched
        #tweepy DOES NOT TAKE IN TIME, so we can ONLY update every day
        tweets = tweepy.Paginator(client.get_users_tweets,id=userID,max_results=50,limit=5,
                                  tweet_fields = ["created_at","author_id"],
                                  start_time = newretrievaldate #veryimpt
                                  )
        
        #for the new tweets that were retrieved,
        for tweet in tweets:   
            if tweet.data == None:
                print('User: ', userID, 'has no new tweets')
                
                #ALWAYS UPDATE when tweets were last retrieved for the user.
                sqlcommand = "UPDATE lastRetrieved SET lastretrieved = %s where Userid = %s"
                with connection.cursor() as cursor:
                    cursor.execute(sqlcommand,(now,userID))
                    connection.commit()
                close_connect()
                print('Userid: ',userID ,' last retrieval date updated with: ', now)
                return
        
        #if he does have new tweets,
            else:
                print('New tweets fetched, getting them into a dataframe')
                for tweet in tweets.flatten(limit=60): 
                    tweetarray.append(tweet.text)
                    tweetidarray.append(tweet.id)
                    tweetauthorarr.append(tweet.author_id)
                    tweetdate.append(tweet.created_at)

                #ALWAYS UPDATE the time of when this users tweets was retrieved
                sqlcommand = "UPDATE lastRetrieved SET lastretrieved = %s where Userid = %s"
                with connection.cursor() as cursor:
                    cursor.execute(sqlcommand,(now,userID))
                    connection.commit()
                close_connect()
                print('Userid: ',userID ,' last retrieval date updated with: ', now)

                #clean his new tweets and put them in a dataframe
                temp_df = pd.DataFrame(zip(tweetidarray,tweetarray,tweetdate,tweetauthorarr),
                                       columns=['tweetid','tweet','tweetdate','authorid'])
                predicted_score = predictHate(temp_df['tweet'])
                temp_df['predicted_score'] = predicted_score  
                temp_df['userID'] = userID
                temp_df['retweet'] = ""
                for row in temp_df.index:
                    checkRT = (temp_df['tweet'].iloc[row])[:2]
                    if checkRT == 'RT':
                        temp_df.iloc[row, temp_df.columns.get_loc('retweet')] = 'true'
                    else:
                        temp_df.iloc[row, temp_df.columns.get_loc('retweet')] = 'false'

                return

            
    else:
        #if this user has NEVER been searched before
        storeTwitteruser(userID)
        print('retrieving Users tweet timeline for the first time, this may take a while!')
        tweets = tweepy.Paginator(client.get_users_tweets,id=userID,max_results=50,limit=5,
                                  tweet_fields = ["created_at","author_id"])
        for tweet in tweets.flatten(limit=60): # Total number of tweets to retrieve
            tweetarray.append(tweet.text)
            tweetidarray.append(tweet.id)
            tweetauthorarr.append(tweet.author_id)
            tweetdate.append(tweet.created_at)
        #record when this user is searched
        newdatetime = dt.now(TZ_sg)
        open_connect()
        sqlcommand = "INSERT INTO lastRetrieved(`Userid`,`lastretrieved`) VALUES(%s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(sqlcommand,(userID,newdatetime))
            connection.commit()
        close_connect()
        print('User: ',userID, 'with a very first retrieval date of: ',newdatetime)
        #PUT ALL his tweets into a dataframe
        print('Putting ALL his tweets into a dataframe')
        temp_df = pd.DataFrame(zip(tweetidarray,tweetarray,tweetdate,tweetauthorarr),
                               columns=['tweetid','tweet','tweetdate','authorid'])
        predicted_score = predictHate(temp_df['tweet'])
        temp_df['predicted_score'] = predicted_score  
        temp_df['userID'] = userID
        temp_df['retweet'] = ""
        for row in temp_df.index:
            checkRT = (temp_df['tweet'].iloc[row])[:2]
            if checkRT == 'RT':
                temp_df.iloc[row, temp_df.columns.get_loc('retweet')] = 'true'
            else:
                temp_df.iloc[row, temp_df.columns.get_loc('retweet')] = 'false'
        
        return temp_df 

#this stores tweets into mysql database
def storetweets(df):
    open_connect()
    sqlcommand = 'INSERT INTO Tweet(TweetID,userID,Tweettext,predictedscore) VALUES (%s,%s,%s,%s)'
    for i in df.index:
        TweetID = df['tweetid'].iloc[i]
        userID = df['userID'].iloc[i]
        Tweettext = df['tweet'].iloc[i]
        predictedscore = df['predicted_hate_score'].iloc[i] 
        with connection.cursor() as cursor:
            try:
                cursor.execute(sqlcommand, (TweetID,userID,Tweettext,predictedscore))
                connection.commit()
            except pymysql.IntegrityError:
                return('tweet with ID: ' + str(TweetID) + ' already exists in database')
    close_connect()

#stores a twitter user into mysql database
def storeTwitteruser(UserID):
    open_connect()
    sqlcommand = 'INSERT INTO `TwitterUser`(`UserID`) VALUES (%s)'
    with connection.cursor() as cursor:
        try:
            cursor.execute(sqlcommand,(UserID))
            connection.commit()
            return('Twitter user with ID: ' + str(UserID) + ' successfully stored in database')
            close_connect()
        except pymysql.IntegrityError:
            return('Twitter user with ID: ' + str(UserID) + ' already exists in database')
            close_connect()

#checks if a user exists within the db
def checkifuserexists(userID):
    open_connect()
    with connection.cursor() as cursor:
        sqlcommand = "SELECT * FROM TwitterUser WHERE EXISTS(SELECT UserID FROM TwitterUser WHERE UserID = %s)"
        cursor.execute(sqlcommand, (userID))
        result = cursor.fetchall()
        close_connect()
        if len(result) == 0:
            return('user !exist')
        else:
            return('user exists!')

def retrieveTweets(twitterhandle):
    tweetarray = []
    tweetidarray = []
    array = []
    temp_df = []
    userID = getuserid(twitterhandle)
    tweets = client.get_users_tweets(id=userID) #checkif user exists 
    if checkifuserexists(userID) == 'user exists!':
        print('user already exists in database, retrieving new tweets!')
        #retrievenewtweets()
    else:
        print('retrieving Users tweet timeline for the first time, this may take a while!')
        temp_df = getalltweets(userID)
        predicted_score = predictHate(temp_df['tweet'])
        temp_df['predicted_hate_score'] = predicted_score  
        temp_df['userID'] = userID
        
    return(temp_df)

def returnScoredtweets(df):
    listofdicttweets = []
    for i in df.index:
        tweet = df['tweet'].iloc[i]
        score = df['predicted_hate_score'].iloc[i]
        dictoftweet = {'tweet' : tweet, 'score': score}
        listofdicttweets.append(dictoftweet)
    
    return listofdicttweets

def analyzeTwitterUser(df):
    hatedf = df[df['predicted_hate_score'] != 2]
    # calculate total number of 0(hateful) + 1(offensive)/total number * 10 = hateful score
    score = round((len(hatedf.index)/len(df.index) * 10),2)

    return score

def returnhatefultweets(df):
    listofdictofhatefultweets = []
    hatedf = df[df['predicted_hate_score'] != 2]
    for i in df.index:
        tweet = df['tweet'].iloc[i]
        score = df['predicted_hate_score'].iloc[i]
        dictoftweet = {'tweet' : tweet, 'score': score}
        listofdictofhatefultweets.append(dictoftweet)
    return listofdictofhatefultweets

def getTweetTypeCount(df):

    offensive = 0
    hateful = 0
    neutral = 0

    for i in df.index:
        score = df['predicted_hate_score'].iloc[i]
        
        if (score == 0):
            offensive +=1
        elif(score == 1):
            hateful += 1
        elif(score == 2):
            neutral += 1

    counts = {'offensive': offensive, 'hateful': hateful ,'total_negative': offensive + hateful, 'neutral': neutral}

    return counts

def getTweetDetails(tweet_id):
    
    tweet = api.get_status(tweet_id)

    return tweet
        
def uploadScoring(filename):
    global df
    global vectorizer 

    df = pd.read_csv(filename)

    test_sentence = df['tweet']
    # expected_result = df['expected']
    df['clean_tweets'] = test_sentence
    
    #expected value form the test case

    x = df['clean_tweets'].values
    y = df['Label'].values 

    expected_Result = predictHate(x)
 

    score = 0
    for row in df.index:
        if expected_Result[row] == y[row]:
          score+=1
    final_score = score/len(df)*100
    return final_score
            