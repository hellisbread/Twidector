import tweepy
import numpy as np
from collections import Counter

from website.config import *

reply_list  = []
like_list = []
mention_list = []

api_key = twitter_key
api_key_secret = twitter_key_secret

access_token = twitter_access
access_token_secret =  twitter_access_secret

auth = tweepy.OAuthHandler(api_key,api_key_secret)
auth.set_access_token(access_token,access_token_secret)

api = tweepy.API(auth)

#establish connection and set bearer token
client = tweepy.Client(bearer_token=twitter_bearer_token)

def assess_replies(twitterHandle):
    accountIDs = []

    #retrieve 100 tweet results
    tweets = api.user_timeline(id = twitterHandle, count = 100)
    for tweet in tweets:
        accountUser = tweet.in_reply_to_user_id
        if(type(accountUser) == int):
            accountIDs.append(accountUser)

        #top 5 users with the most number of replies
    results = Counter(accountIDs).most_common(10)

        #return list of profiles that are close to user
    list_of_users = []
    for result in results:
        list_of_users.append(result[0])
    return list_of_users

def assess_other_replies(results):
    if(len(results) > 0):
        for result in results:
            reply_list.append(assess_replies(result))


def assess_replies_score(UserID):
    potential_close_friends = []

    #retrieve top 5 users that the TwitterHandle replied
    result_list_of_users = assess_replies(UserID)

    #retrieve their top 5 users that repliers replied to
    assess_other_replies(result_list_of_users)

    count = 0
    for user in result_list_of_users:
        if (user in reply_list[count]):
            potential_close_friends.append(user)
        count += 1

    if (UserID in potential_close_friends):
        potential_close_friends.remove(UserID)

    return potential_close_friends

def assess_following(UserID):

    list_of_following = []
    following = client.get_users_following(id = UserID, max_results=1000)
    for user in following.data:
        list_of_following.append(user.id)
    
    return list_of_following

def assess_mentions(UserID):
    authorID_list = []
    topFive_authors = []

    responses = client.get_users_mentions(id = UserID, max_results = 50, expansions = 'author_id')
    count = 0 
    while count < len(responses.data):
        try:
            authorID_list.append(responses.data[count].author_id)
        except:
            continue
        count += 1 

    #top 5 authors that mention the user the most
    results = Counter(authorID_list).most_common(10)
    for result in results:
        topFive_authors.append(result[0])
        
    return topFive_authors
    
def assess_other_mentions(results):
    for result in results:
            mention_list.append(assess_mentions(result))

def assess_mention_score(UserID):
    potential_close_friends = []

    #retrieve top 5 users that the TwitterHandle replied
    result_list_of_users = assess_mentions(UserID)

    #retrieve their top 5 users that repliers replied to
    assess_other_mentions(result_list_of_users)

    count = 0
    for user in result_list_of_users:
        if (user in mention_list[count]):
            potential_close_friends.append(user)
        count += 1
    if (UserID in potential_close_friends):
        potential_close_friends.remove(UserID)
    return potential_close_friends

def assess_relationship(TwitterHandle):
    Account = client.get_user(username = TwitterHandle)
    UserID = Account.data.id

    following_list = assess_following(UserID)
    reply_score = (assess_replies_score(UserID))
    mention_score = (assess_mention_score(UserID))
    total_score = reply_score + mention_score
    results = Counter(total_score)
    for user in total_score:
        if(user in following_list):
            results[user] += 1

    return results

assess_relationship("Ballislife")