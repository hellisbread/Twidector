import tweepy
import numpy as np
from collections import Counter

from website.config import *
from .models import Favourited, Blocked

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

def updateAccess(user_access_token, user_secret):
    try:
        auth.set_access_token(user_access_token, user_secret)
        return True
    except:
        return False

def assess_replies(twitterHandle):
    accountIDs = []

    #retrieve 100 tweet results
    try:
        tweets = api.user_timeline(user_id = twitterHandle, count = 100)
        for tweet in tweets:
            accountUser = tweet.in_reply_to_user_id
            if(type(accountUser) == int):
                accountIDs.append(accountUser)

        #top 10 users with the most number of replies
        results = Counter(accountIDs).most_common(10)

            #return list of profiles that are close to user
        list_of_users = []
        for result in results:
            list_of_users.append(result[0])
        return list_of_users
    except:
        return []

def assess_other_replies(results):
    if(len(results) > 0):
        for result in results:
            reply_list.append(assess_replies(result))


def assess_replies_score(UserID):

    potential_close_friends = []

    #retrieve top 5 users that the TwitterHandle replied
    result_list_of_users = assess_replies(UserID)

    if not result_list_of_users:
        return []
    else:
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
    responses= client.get_users_following(id = UserID, max_results=1000)
    count = 0
    for tweets in responses:
        if tweets is None:
            continue
        else:
            try:
                for tweet in tweets:
                    list_of_following.append(tweet['id'])
            except TypeError:
                break
    return list_of_following

def assess_followers(UserID):
    list_of_followers = []
    responses = client.get_users_followers(id = UserID, max_results = 1000)
    for tweets in responses:
        if tweets is None:
            continue
        else:
            try:
                for tweet in tweets:
                    list_of_followers.append(tweet['id'])
            except TypeError:
                break
    return list_of_followers

def assess_mentions(UserID):
    authorID_list = []
    topFive_authors = []

    responses = client.get_users_mentions(id = UserID, max_results = 100, expansions = 'author_id')
    count = 0
    for tweets in responses:
        if tweets is None:
            continue
        else:
            try:
                for tweet in tweets:
                    authorID_list.append(tweet['author_id'])
            except TypeError:
                break
    
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
    dict_score = {}
    following_each_other = []

    Account = client.get_user(username = TwitterHandle)
    UserID = Account.data.id
    follower_list = assess_followers(UserID)
    following_list = assess_following(UserID)
    reply_score = (assess_replies_score(UserID))
    mention_score = (assess_mention_score(UserID))
    
    #1st:(following each other + mentions), 2nd:(following each other + reply), 3rd: following each other, 4th: mentions only, 5th: reply only  
    #evaluate if users are following each other
    for user in following_list:
        if user in follower_list:
            following_each_other.append(user)
    
    total_list = following_each_other + reply_score + mention_score
    total_list = np.array(total_list)
    total_list = np.unique(total_list)  
    
    for user in total_list:
         dict_score[user] = 0
         if user in following_each_other and user in mention_score:
             dict_score[user] = dict_score[user] + 5
         if user in following_each_other and user in reply_score:
             dict_score[user] = dict_score[user] + 4
         if user in following_each_other:
             dict_score[user] = dict_score[user] + 3
         if user in mention_score:
             dict_score[user] = dict_score[user] + 2
         if user in reply_score:
             dict_score[user] = dict_score[user] + 1
        
    return dict_score

def score_relationship(dict_score, user_request):

    blocked_objectlist = Blocked.objects.filter(user = user_request).filter(soft_delete=0).values_list('blocked_twitter_id', 'blocked_username')
    favourited_objectlist = Favourited.objects.filter(user = user_request).filter(soft_delete=0).values_list('favourited_twitter_id', 'favourited_username')

    print(blocked_objectlist)
    print(favourited_objectlist)

    list = dict_score.keys()
    result_list = []
    for userid in list:
        user_list = []
        Response  = client.get_user(id = userid, user_fields=['profile_image_url'])

        imageUrl = Response.data.profile_image_url
        user_list.append(Response.data.id)
        user_list.append(Response.data.username)
        user_list.append(dict_score[Response.data.id])
        user_list.append(imageUrl.replace("_normal", ""))
        result_list.append(user_list)

    return result_list

def retrieve_top_users(dict_score , x , user_request):
    results = Counter(dict_score).most_common(x)
    results_list = list(sum(results, ()))
    result_dict  = {results_list[i]: results_list[i+1] for i in range(0, len(results_list), 2)}
    final_result = score_relationship(result_dict,user_request)

    return final_result