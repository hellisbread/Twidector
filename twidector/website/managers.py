from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _

class CustomUserManager(BaseUserManager):

    def create_user(self, username, password, email, twitter_oauth_token, **extra_fields):

        if not username:
            raise ValueError(_('The username must be set'))
        username = self.set_username
        email = self.normalize_email(email)
        twitter_oauth_token = self.model(twitter_oauth_token) or None
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user