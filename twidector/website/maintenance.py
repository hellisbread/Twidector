import pandas as pd
import datetime
import time

from .hatedetection import *
from .models import Tweet

def sql_to_dataframe_hate():

    query_set = Tweet.objects.filter(fitted_hate=False)
    

def retrain(dataframe):
    #load from file saved model
    clf = load_model()
    
    cleaned_tweets = preprocess(dataframe)
    df['clean_tweet'] = cleaned_tweets
    y = df["class"].values
    x = df["clean_tweet"].values
    
    vectorizer = load_vectorizer('hate_vectorizer.sav')
    
    vectorizer.fit(list(x))
    
    x_train_vec = vectorizer.transform(x_train)

    clf = linear_model.SGDClassifier(max_iter=1000)
    
    clf.partial_fit(x_train_vec, y)
    
    #save into file model
    save_model(clf)