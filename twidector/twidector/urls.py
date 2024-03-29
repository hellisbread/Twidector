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
    path('login/', views.login_view, name='login'),
    path('login_twitter/', views.login_twitter, name='login_twitter'),
    path('login_twitter_callback/', views.login_twitter_callback, name='login_twitter_callback'),
    path('sync_twitter/', views.sync_twitter, name='sync_twitter'),
    path('sync_twitter_callback/', views.sync_twitter_callback, name='sync_twitter_callback'),
    path('deactivate_account/', views.deactivate_account, name='deactivate_account'),
    path('deactivate_account_true/', views.deactivate_account_true, name='deactivate_account_true'),
    path('deactivate_account_false/', views.deactivate_account_false, name='deactivate_account_false'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('forgot-password/', views.forgotPassword, name='forgot-password'),
    #path('forgot-username/', views.forgotUsername, name='forgot-username'),
    path('free-trial/', views.freeTrial, name='free-trial'),
    #path('reset-password/', views.resetPassword, name='reset-password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analyse/', views.analyse, name='analyse'),
    path('analyse/<str:user_handle>/', views.AnalyzeUser, name='analyzeUser'),
    path('report-tweet/', views.reportTweets, name='report-tweet'),
    path('view-tweet/', views.viewTweet, name='view-tweet'),
    path('block-list/', views.blocklist, name='block-list'),
    path('block-list/add/<str:user_id>/', views.add_blocklist, name='add-block-list'),
    path('block-list/delete/<str:user_id>/', views.delete_blocklist, name='delete-block-list'),
    path('favourites/', views.favouritelist, name='favourites'),
    path('favourites/add/<str:user_id>/', views.add_favouritelist, name='add-favourites'),
        path('favourites/delete/<str:user_id>/', views.delete_favouritelist, name='delete-favourites'),
    path('settings/',views.settings,name='settings'),
    path("update_server/", views.update, name="update"),
    path('admin/accuracy-score/', views.accuracyScore, name='accuracy-score'),
    path('admin/home/', views.adminPage, name='admin-page'),
    path('admin/search-account/', views.searchAccount, name='search-account'),
    path('admin/update-user/<str:user_id>/', views.updateUser, name='update-user'),
    path('admin/delete-user/<str:user_id>/', views.delete_user, name='delete-user'),
    path('admin/file-upload/', views.file_upload, name='file-upload'),
    path('admin/drop-file/', views.drop_file, name='drop-file'),
    path('admin/', views.adminLogin, name='admin'),
    path('admin/ascore-fn/', views.ascore_fakenews, name='ascore-fn'),
    path('admin/model-testing', views.modelTesting, name='model-testing'),
    path('admin/reported-tweets/', views.reportedTweets, name='reported-tweets'),
    path('admin/accessing-score/', views.accessing_score, name='accessing-score'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    #path('password_reset_form/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html', html_email_template_name='password_reset_email.html'), name='password_reset_form'),
    path('password_reset_form/', views.password_reset_form, name='password_reset_form'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name = 'password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    #path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    #path('admin/', admin.site.urls),
]
