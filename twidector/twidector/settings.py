"""
Django settings for twidector project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
#from decouple import config

import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['twidector.pythonanywhere.com','localhost','127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'twidector',
    'website',
    'django_extensions', #delete this eventually
    'crispy_forms',
]
CRISPY_TEMPLATE_PACK = 'uni_form'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'twidector.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

WSGI_APPLICATION = 'twidector.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

from sshtunnel import SSHTunnelForwarder

ssh_tunnel = SSHTunnelForwarder(
    "ssh.pythonanywhere.com",
    ssh_username = "twidector",
    ssh_password = "SIMfypTopic18",
    remote_bind_address = ('twidector.mysql.pythonanywhere-services.com', 3306)
)
ssh_tunnel.start()

DATABASES = {
    #production settings
    'default': {
        'ENGINE': os.getenv('PROD_SQL_ENGINE'),
        'NAME': os.getenv('PROD_SQL_NAME'),
        'USER': os.getenv('PROD_SQL_USER'),
        'PASSWORD': os.getenv('PROD_SQL_PASSWORD'),
        'HOST': os.getenv('PROD_SQL_HOST'),
    }
}

"""
    #production settings
    'default': {
        'ENGINE': os.getenv('PROD_SQL_ENGINE'),
        'NAME': os.getenv('PROD_SQL_NAME'),
        'USER': os.getenv('PROD_SQL_USER'),
        'PASSWORD': os.getenv('PROD_SQL_PASSWORD'),
        'HOST': os.getenv('PROD_SQL_HOST'),
    }
"""
"""
    #development settings
    'default': {
        'ENGINE': os.getenv('DEV_SQL_ENGINE'),
        'NAME': os.getenv('DEV_SQL_NAME'),
        'USER': os.getenv('DEV_SQL_USER'),
        'PASSWORD': os.getenv('DEV_SQL_PASSWORD'),
        'HOST': os.getenv('DEV_SQL_HOST'),
        'PORT': ssh_tunnel.local_bind_port,
        'TEST': {
          'NAME': "twidector$default",
        },
        'OPTIONS': {
            'sql_mode': 'traditional',
        }
    }
"""

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

#AUTH_USER_MODEL = 'website.CustomTwidectorUser'

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Singapore'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'

# disable for localhost testing
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = SERVER_EMAIL = EMAIL_HOST_USER = os.getenv('DEFAULT_FROM_EMAIL')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

#TWITTER SETTINGS
TWITTER_API_KEY=os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET=os.getenv('TWITTER_API_SECRET')
TWITTER_CLIENT_ID=os.getenv('TWITTER_CLIENT_ID')
TWITTER_CLIENT_SECRET=os.getenv('TWITTER_CLIENT_SECRET')
TWITTER_OAUTH_CALLBACK_URL=os.getenv('TWITTER_OAUTH_CALLBACK_URL')