import pandas as pd
import datetime
import time
import csv
from .hatedetection import *
from .models import Tweet, FakeNews
from bs4 import BeautifulSoup
import urllib.request,sys,time
import requests
from dateutil.parser import parse

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

def new_hate_data():
    result = Tweet.objects.filter(admin_interjection=True, predicted_hate_score__isnull=False).values('tweet_id', 'tweet_text', 'admin_hate_result', 'fitted_hate')
    with open(r'hatedetectioncleaned.csv', 'a', newline='') as csvfile:
        fieldnames = ['tweet_text','hate_score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for item in result.iterator():
            if item['fitted_hate'] == 0:
                cur_tweet = Tweet.objects.filter(tweet_id=item['tweet_id'])
                cur_tweet.update(fitted_hate = 1)
                writer.writerow({'tweet_text':item['tweet_text'], 'hate_score':item['admin_hate_result']})

new_hate_data()

def new_fake_data():
    result = FakeNews.objects.filter().values('fake_news_text', 'fake_news_score', 'date_time')
    with open(r'fakenewscleaned.csv', 'w', newline='') as csvfile:
        fieldnames = ['fake_news_text','fake_news_score', 'date_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for item in result.iterator():
            writer.writerow({'fake_news_text':item['fake_news_text'], 'fake_news_score':item['fake_news_score'], 'date_time':item['date_time']})
            print(item)

new_fake_data()

def retrain():
    df = pd.read_csv('hatedetectioncleaned.csv')
    #load from file saved model
    #clf = load_pickle('hate_model.sav')

    y = df["hate_score"].values
    x = df["tweet_text"].values
    
    x_train = x

    #vectorizer = load_pickle('hate_vectorizer.sav')
    
    vectorizer = CountVectorizer(ngram_range=(1, 4), max_features = 1000)
    vectorizer.fit(list(x))

    
    x_train_vec = vectorizer.transform(x_train)

    clf = linear_model.SGDClassifier(max_iter=1000)
    
    clf.fit(x_train_vec, y)
    
    #save into file model
    save_pickle(clf,'hate_model.sav')

    save_pickle(vectorizer,'hate_vectorizer.sav')

retrain()