import pandas as pd
import datetime
import time
import csv
from .hatedetection import *
from .fakenews import cleanStatements
from .models import Tweet, FakeNews
from bs4 import BeautifulSoup
import urllib.request,sys,time
import requests
from dateutil.parser import parse
import pickle

from sklearn.feature_extraction.text import CountVectorizer
from sklearn import linear_model

def save_pickle(model, filename):
    pickle.dump((model), open(filename, 'wb'))

def load_pickle(filename):
    picklefied = pickle.load(open(filename, 'rb'))
    
    return picklefied

#retrieve the latest date in fakenewscleaned table
def LatestDate():
    data = pd.read_csv('fakenewscleaned.csv', encoding="ISO-8859-1")
    data['Date'] = pd.to_datetime(data['Date'])
    latest_date = data['Date'].max()
    return latest_date

#retrieve latest news    
def webscrape_data():
    
    list_of_date = []
    frame = []
    
    #fetch the latest date in stored db
    fetch_date = LatestDate()
    
    #fetch_date = strptime
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
            if label == 'true':
                label = 'TRUE'
            elif label == 'false':
                label = 'FALSE'
            Statement = j.find("div", attrs = {'class' : 'm-statement__quote'}).text.strip()
            frame.append((Statement, label, Date))
    
    data = pd.DataFrame(frame, columns=['Statement', 'Label', 'Date'])
    
    if not data.empty:
        #clean the statements
        clean_statements = cleanStatements(data["Statement"])
        data['Statement'] = clean_statements

        data.to_csv("fakenewscleaned.csv", header = False, index = False, mode = 'a')


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

#new_hate_data()

# def new_fake_data():
#     result = FakeNews.objects.filter().values('fake_news_text', 'fake_news_score', 'date_time')
#     with open(r'fakenewscleaned.csv', 'w', newline='', encoding = 'utf-8') as csvfile:
#         fieldnames = ['fake_news_text','fake_news_score', 'date_time']
#         writer = csv.writer(csvfile)
#         writer.writerow(fieldnames)
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#         for item in result.iterator():
#             writer.writerow({'fake_news_text':item['fake_news_text'], 'fake_news_score':item['fake_news_score'], 'date_time':item['date_time']})
#             print(item)

#new_fake_data()

def retrain_hate():
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

