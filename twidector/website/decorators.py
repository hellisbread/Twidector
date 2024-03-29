from functools import wraps
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from website.authorization import check_token_still_valid
from .models import TwitterUser


def twitter_login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        twitter_user = TwitterUser.objects.filter(user=request.user).first()
        info = check_token_still_valid(twitter_user)
        if info is None:
            logout(request)
            return HttpResponseRedirect(reverse('login_twitter'))
        else:
            return function(request, *args, **kwargs)
    return wrap