import pandas as pd
import datetime
import time
import csv
from .hatedetection import *
from .models import Tweet

def new_hate_data():
    result = Tweet.objects.filter(admin_interjection=True).values('tweet_id', 'tweet_text', 'admin_hate_result', 'fitted_hate')

    with open(r'hatedetectioncleaned.csv', 'a', newline='') as csvfile:
        fieldnames = ['tweet_text','hate_score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for item in result.iterator():
            if item['fitted_hate'] == 0:
                cur_tweet = Tweet.objects.filter(tweet_id=item['tweet_id'])
                cur_tweet.update(fitted_hate = 1)
                writer.writerow({'tweet_text':item['tweet_text'], 'hate_score':item['admin_hate_result']})


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