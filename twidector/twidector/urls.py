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
from django.contrib.auth import views as auth_views

from website import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about-us/',views.aboutUs, name='about-us'),
    path('about-team/', views.aboutTeam, name='about-team'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('login_twitter/', views.login_twitter, name='login_twitter'),
    path('login_twitter_callback/', views.twitter_callback, name='twitter_callback'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('forgot-password/', views.forgotPassword, name='forgot-password'),
    #path('forgot-username/', views.forgotUsername, name='forgot-username'),
    path('free-trial/', views.freeTrial, name='free-trial'),
    #path('reset-password/', views.resetPassword, name='reset-password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analyse/', views.analyse, name='analyse'),
    path('analyse-2/', views.analyseTwo, name='analyse-2'),
    path('view-tweet/', views.viewTweet, name='view-tweet'),
    path('blacklist/', views.blacklist, name='blacklist'),
    path('whitelist/', views.whitelist, name='whitelist'),
    path('settings/',views.settings,name='settings'),
    path("update_server/", views.update, name="update"),
    path('admin/accuracy-score/', views.accuracyScore, name='accuracy-score'),
    path('admin/home/', views.adminPage, name='admin-page'),
    path('admin/search-account/', views.searchAccount, name='search-account'),
    path('admin/update-user/<str:user_id>/', views.updateUser, name='update-user'),
    path('admin/delete-user/<str:user_id>/', views.delete_user, name='delete-user'),
    path('admin/', views.adminLogin, name='admin'),
    path('admin/model-testing', views.modelTesting, name='model-testing'),
    path('admin/reported-tweets', views.reportedTweets, name='reported-tweets'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('password_reset_form/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html', html_email_template_name='password_reset_email.html'), name='password_reset_form'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name = 'password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    #path('admin/', admin.site.urls),
]
