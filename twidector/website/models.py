from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class CustomTwidectorUser(AbstractUser):
    username = models.CharField(max_length=191, unique=True)
    email = models.EmailField(max_length=191, unique=True)
    password = models.CharField(max_length=100)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = 'website_user'

