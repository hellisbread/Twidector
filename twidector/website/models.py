from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class TwitterAuthToken(models.Model):
    oauth_token = models.CharField(max_length=255)
    oauth_token_secret = models.CharField(max_length=255)

    def __str__(self):
        return self.oauth_token
        
class CustomTwidectorUser(AbstractUser):
    username = models.CharField(max_length=191, unique=True)
    email = models.EmailField(max_length=191, unique=True, null=True)
    password = models.CharField(max_length=128, null=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"

    class Meta:
        db_table = 'website_user'

class TwitterUser(models.Model):
    twitter_id = models.CharField(max_length=255)
    screen_name = models.CharField(max_length=255)
    twitter_oauth_token = models.ForeignKey(TwitterAuthToken, on_delete=models.CASCADE)
    user = models.ForeignKey('CustomTwidectorUser', on_delete=models.CASCADE)

    def __str__(self):
        return self.screen_name

    class Meta:
        db_table = 'website_twitter_user'

class LastRetrieved(models.Model):
    twitter_id = models.CharField(max_length=255, primary_key=True)
    last_retrieved = models.DateTimeField(null = True)

    class Meta:
        db_table = 'last_retrieved'

class Tweet(models.Model):
    tweet_id = models.IntegerField(primary_key=True)
    user_id = models.CharField(max_length=20, null=True)
    tweet_date = models.DateTimeField(null = True)
    tweet_text = models.TextField(null = True)
    predicted_score = models.CharField(max_length=1)
    flagged = models.CharField(max_length=1)
    retweet = models.CharField(max_length=5)

    class Meta:
        db_table = 'tweet'

class ReportedTweet(models.Model):
    reported_id = models.IntegerField(primary_key=True, unique=True)
    reported_status = models.SmallIntegerField()
    tweet_id = models.IntegerField(unique=True)
    report_date = models.DateTimeField(null = True)

    class Meta:
        db_table = 'reported_tweet'

class TwitterUserScore(models.Model):
    twitter_id = models.CharField(max_length=255, primary_key=True)
    hate_score = models.IntegerField()
    fake_news_score = models.IntegerField()

    class Meta:
        db_table = 'twitter_user_score'
