from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.
class TwitterAuthToken(models.Model):
    oauth_token = models.CharField(max_length=255)
    oauth_token_secret = models.CharField(max_length=255)

    def __str__(self):
        return self.oauth_token

    class Meta:
        db_table = 'website_twitter_auth_token'

class TwitterUser(models.Model):
    twitter_id = models.CharField(max_length=255)
    screen_name = models.CharField(max_length=255)
    twitter_oauth_token = models.ForeignKey(TwitterAuthToken, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.screen_name

    class Meta:
        db_table = 'website_twitter_user'

# class SearchedUser(models.Model):
#     twitter_id = models.CharField(max_length=255, primary_key=True)
#     last_retrieved = models.DateTimeField(null = True)

#     class Meta:
#         db_table = 'last_retrieved'

class Tweet(models.Model):
    tweet_id = models.CharField(primary_key=True, max_length=255)
    screen_name = models.CharField(max_length=255)
    tweet_date = models.DateTimeField(null = True)
    tweet_text = models.TextField(null = True)
    predicted_hate_score = models.CharField(max_length=1, null=True)
    predicted_fake_score = models.CharField(max_length=1, null=True)
    retweet = models.CharField(max_length=5, null=True)
    flagged = models.CharField(max_length=1, default=0)
    offensive_count = models.IntegerField(default=0)
    hateful_count = models.IntegerField(default=0)
    neutral_count = models.IntegerField(default=0)
    fake_news_count = models.IntegerField(default=0)
    admin_interjection = models.BooleanField(default = False)
    admin_hate_result = models.CharField(max_length=1, null=True)
    admin_news_result = models.CharField(max_length=1, null=True)
    fitted_hate = models.BooleanField(default = False)
    fitted_news = models.BooleanField(default = False)

    class Meta:
        db_table = 'tweet'

class TwitterUserScore(models.Model):
    twitter_id = models.CharField(max_length=255, primary_key=True)
    hate_score = models.IntegerField()
    fake_news_score = models.IntegerField()
    last_retrieved = models.DateTimeField(default=now)

    class Meta:
        db_table = 'twitter_user_score'

class FakeNews(models.Model):
    fake_news_text = models.TextField()
    fake_news_score = models.BooleanField()
    date_time = models.DateTimeField(default=now, blank=True)

    class Meta:
        db_table = 'fake_news_score'

class Hate(models.Model):
    tweet_text = models.TextField()
    hate_score = models.IntegerField()

    class Meta:
        db_table = 'hate_score'

class SyncTwitterAccount(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    twitter_id = models.CharField(max_length=255)

    class Meta:
        db_table = 'sync_twitter'

class Favourited(models.Model):
    favourited_twitter_id = models.CharField(max_length=255)
    favourited_username = models.CharField(max_length=255)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    soft_delete = models.BooleanField()

    class Meta:
        db_table = 'favourited'

class Blocked(models.Model):
    blocked_twitter_id = models.CharField(max_length=255)
    blocked_username = models.CharField(max_length=255)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    soft_delete = models.BooleanField()

    class Meta:
        db_table = 'blocked'



