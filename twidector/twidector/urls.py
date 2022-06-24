"""twidector URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from website import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about-us/',views.aboutUs, name='about-us'),
    path('about-team/', views.aboutTeam, name='about-team'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('forgot-password/', views.forgotPassword, name='forgot-password'),
    path('free-trial/', views.freeTrial, name='free-trial'),
    path('free-trial-2/', views.freeTrialTwo, name='free-trial-2'),
    path('reset-password/', views.resetPassword, name='reset-password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analyse/', views.analyse, name='analyse'),
    path('analyse-2/', views.analyseTwo, name='analyse-2'),
    path('view-tweet/', views.viewTweet, name='view-tweet'),
    path('blacklist/', views.blacklist, name='blacklist'),
    path('whitelist/', views.whitelist, name='whitelist'),
    path('settings/',views.settings,name='settings'),
    #path('admin/', admin.site.urls),
]
