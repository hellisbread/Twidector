#from django.contrib import admin
#from django.contrib.auth.admin import UserAdmin
#from .models import CustomTwidectorUser
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

# Register your models here.

#admin.site.register(CustomTwidectorUser, UserAdmin)

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = User.objects.using(request.GET['auth_user']).filter(username=username)
        if user.check_password(password) and self.user_can_authenticate(user):
            return user