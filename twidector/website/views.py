#import git
from wsgiref import validate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from pymysql import NULL
from .decorators import twitter_login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.messages.views import SuccessMessageMixin

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

#from website.models import CustomTwidectorUser

from .forms import user_info

from .forms import UserRegistrationForm
from django.contrib.auth import views as auth_views
from django.contrib.admin.views.decorators import staff_member_required

from .tokens import account_activation_token
#from django.contrib.auth.models import User
#from django.core.mail import EmailMessage

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
#from django.utils import six
#from django.contrib.auth import login, authenticate
#from django.contrib.auth.models import User
#from django.core.mail import EmailMessage
from django.core.mail import send_mail, BadHeaderError

from django.contrib.auth import get_user_model

user = get_user_model()
from .models import TwitterAuthToken, TwitterUser

from website.functions import *
from website.hatedetection import *

from website.twitter_api import TwitterAPI
from website.authorization import create_update_user_from_twitter, check_token_still_valid

@csrf_exempt

def update(request):
    if request.method == "POST":
        
        #repo = git.Repo("twidector.pythonanywhere.com/") 
        #origin = repo.remotes.origin

        #origin.pull()

        return HttpResponse("Updated code on PythonAnywhere")
    else:
        return HttpResponse("Couldn't update the code on PythonAnywhere")

# Create your views here.
def index(request):
    return render(request,'index.html',{})

def aboutUs(request):
    return render(request,'about-us.html',{})

def aboutTeam(request):
    return render(request,'about-team.html',{})

def freeTrial(request):

    context = {}

    if request.method == 'POST':

        url = request.POST['twitter-url']

        prepareDF()

        twitterID = getuserid(url)

        twitterIMGURL = getuserIMG(twitterID)

        data = getalltweets(twitterID, 200)

        predicted_score = predictHate(data['tweet'])
        data['predicted_score'] = predicted_score  
        data['userID'] = twitterID

        hateCount = getHatefulTweetCount(data)

        context = {'dataframe': data , 'user' : url, 'img' : twitterIMGURL, 'hateCount' : hateCount}

        print(context)

        return render(request, 'free-trial.html', context)
    else:
        return render(request, 'free-trial.html', context)

#Login/Register Views
@login_required
@twitter_login_required
def login(request):
    if 'loggedin' not in request.session:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            request.session['loggedin'] = username
            auth_login(request, user)
            return redirect('dashboard')
            
        else:
            messages.error(request, 'Invalid Username or Password')
            return redirect('login')
    else:
        return redirect('index')

@login_required
def logout(request):
    if 'loggedin' not in request.session:

        return redirect('login')

    else:
        del request.session['loggedin']
        auth_logout(request)
        messages.success(request, 'Successfully Logged out.')
        return redirect('login')

def register(request):

    if 'loggedin' not in request.session:
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            #username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password1')
            passwordcheck = request.POST.get('password2')
            #usertype = 0

            if(password != passwordcheck):
                messages.error(request, 'Error. Password does not match.')
                return redirect('register')

            if form.is_valid():
                user = get_user_model()
                user = form.save(commit=False)
                user.is_active = False
                #user.is_staff = True
                user.save()  
                current_site = get_current_site(request)
                subject = "Twidector Account Activation"
                message = render_to_string('activate_account_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':account_activation_token.make_token(user),
                'protocol': 'http',
            })
                try:
                    send_mail(subject, message, 'twidector@gmail.com' , [user.email], fail_silently=False, html_message=message)
                    messages.success(request, 'Successfully created account. Please activate your account through the link sent to the email.')
                    return redirect('login')

                except:
                    return HttpResponse('Invalid header found.')

            else:
                for msg in form.error_messages:
                    messages.error(request, f"{msg}: {form.error_messages[msg]}")
                    print(msg)  

        form = UserRegistrationForm()

        return render(request, 'register.html', {'form':form})
            
    else:
        return redirect('index')

#def activate(request):
    #return render(request, 'Activate.html')

def activate(request, uidb64, token):
    user = get_user_model()  
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = user.objects.get(pk=uid)  
        
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        # return redirect('home')
        messages.success(request,'Successfully activated account')
        return redirect('login')
    else:
        messages.error('Activation link invalid.')
        return redirect('login')

def forgotPassword(request):

    return render(request, 'forgot-password.html', {})


def password_reset_form(request):

    if request.method == 'POST':
        #form = PasswordResetForm(request.POST)
        form = auth_views.PasswordResetView(request.POST)
        email = request.POST.get('email')
        
        if form.is_valid():
            user = get_user_model()
            user = form.save(commit=False)
            user.set_unusable_password()
            user.is_active = True
            user.save()  
            current_site = get_current_site(request)
            subject = "Twidector Password Reset Requested"
            message = render_to_string('password_reset_email.html', {
            'email' : user.email,    
            'user': user,
            'domain': current_site.domain,
            'site_name': 'Twidector',
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
            'token':account_activation_token.make_token(user),
            'protocol': 'http',
        })
            try:
                send_mail(subject, message, 'twidector@gmail.com' , [user.email], fail_silently=False, html_message=message)
                messages.success(request, 'Successfully sent to email on how to reset password')
                return redirect('login')
            except:
                return HttpResponse('Invalid header found.')

    form = auth_views.PasswordResetView()

    return render(request, 'password_reset_form.html', {'form':form})


def resetForgotPassword(request):

    return render(request, 'resetForgotPassword ', {})


#def password_reset_confirm(request, uidb64, token):
    user = get_user_model()  
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = user.objects.get(pk=uid)  
        
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password1')
            passwordcheck = request.POST.get('password2')

            if(password != passwordcheck):
                messages.error(request, 'Error. Password does not match.')

            reset_user_password(user.email, password)

        # return redirect('home')


        return render(request, 'resetForgotPassword ', {})

    else:
        return HttpResponse('Reset link is invalid!')

#def resetPassword(request):
    return render(request, 'reset-password.html', {})

#def forgotUsername(request):
    return render(request, 'forgot-password.html', {})
    
def login_twitter(request):
    twitter_api = TwitterAPI()
    url, oauth_token, oauth_token_secret = twitter_api.twitter_login()
    if url is None or url == '':
        messages.error('Error.')
        return redirect('index')
    else:
        twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
        if twitter_auth_token is None:
            twitter_auth_token = TwitterAuthToken(oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
            twitter_auth_token.save()
        else:
            twitter_auth_token.oauth_token_secret = oauth_token_secret
            twitter_auth_token.save()
        return redirect(url)


def twitter_callback(request):
    if 'denied' in request.GET:
        messages.error('Error.')
        return redirect('index')
    twitter_api = TwitterAPI()
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_token = request.GET.get('oauth_token')
    twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
    if twitter_auth_token is not None:
        access_token, access_token_secret = twitter_api.twitter_callback(oauth_verifier, oauth_token, twitter_auth_token.oauth_token_secret)
        if access_token is not None and access_token_secret is not None:
            twitter_auth_token.oauth_token = access_token
            twitter_auth_token.oauth_token_secret = access_token_secret
            twitter_auth_token.save()
            # Create user
            info = twitter_api.get_me(access_token, access_token_secret)
            if info is not None:
                twitter_user_new = TwitterUser(twitter_id=info[0]['id'], screen_name=info[0]['username'])
                twitter_user_new.twitter_oauth_token = twitter_auth_token
                user, twitter_user_new = create_update_user_from_twitter(twitter_user_new)
                if user is not None:
                    auth_login(request, user)
                    return redirect('dashboard')
            else:
                messages.error('Error.')
                return redirect('index')
        else:
            messages.error('Error.')
            return redirect('index')
    else:
        messages.error('Error.')
        return redirect('index')

#Admin Views
def adminLogin(request):
    if 'adminlog' not in request.session:
        if request.method == 'POST':
            username  = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                request.session['loggedin'] = username
                auth_login(request, user)
                messages.success(request, 'Successfully Login to Admin Panel')
                return redirect('search-account')
                
            else:
                messages.error(request, 'Invalid Username or Password')
                return redirect('adminLogin')

        else:
            return render(request,'admin-login.html', {})
    else:
        return redirect('index')

def accuracyScore(request):
    return render(request, 'accuracy-score.html', {})

def adminPage(request):
    return render(request, 'admin-page.html', {})

@staff_member_required
def searchAccount(request):

    #retrieve the user from the database
    
    if request.method == "POST":
        user = get_user_model()
        #user input
        searched = request.POST['searched']
        user = user.objects.filter(username__icontains= searched)

        if user:
            messages.success(request, 'Successfully Found!')
            return render(request, 'search-account.html' ,{'searched' : searched, 'user': user})
            
        else:
            messages.error(request,"Sorry! No user found!")
            return render(request, 'search-account.html' , {})

    else:
        return render(request, 'search-account.html' , {})


def updateUser(request,user_id):

    user = get_user_model()
    #getting the id for each user
    user = user.objects.get(pk = user_id)
    form = user_info(request.POST or None, instance=user)

    if form.is_valid():
        form.save()
        return redirect('search-account')

    return render(request, 'update-user.html', {'user' : user, 'form' : form})

def delete_user(request,user_id):
    user = get_user_model()
    #getting the id for each user
    user = user.objects.get(pk = user_id)
    user.delete()
    return render(request, 'search-account.html' , {})

def modelTesting(request):
    return render(request, 'model-testing.html', {})

def reportedTweets(request):
    return render(request, 'reported-tweets.html', {})

#Dashboard Views
@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {})

@login_required
def analyse(request):
    return render(request, 'analyse.html', {})

@login_required
def analyseTwo(request):
    return render(request, 'analyse-2.html', {})

@login_required
def viewTweet(request):
    return render(request, 'view-tweet.html', {})

@login_required
def blacklist(request):

    context = {}

    loggedUser = request.session.get('loggedin')

    #Retrieve List
    blacklisted_users = retrieve_blacklist(loggedUser)

    #Convert List to context dict
    list_of_blacklisted_users = []
    for user in blacklisted_users:
        list_of_blacklisted_users.append(user)

    context['list_of_blacklisted_users'] = list_of_blacklisted_users

    #POST
    if request.method == 'POST':
        #Add new blacklisted user
        blacklist_username = request.POST['blacklist-user']

        result = blacklist_user(loggedUser , blacklist_username)

        if result:
            messages.success(request, "Successfully blacklisted " + blacklist_username)
        else:
            messages.error(request, "This username exists in your blacklist.")

        return redirect('blacklist')

    else:
        
        return render(request, 'blacklist.html', context)

@login_required
def whitelist(request):

    context = {}

    loggedUser = request.user.id

    #Retrieve List
    whitelisted_users = retrieve_whitelist(loggedUser)

    #Convert List to context dict
    list_of_whitelisted_users = []
    for user in whitelisted_users:
        list_of_whitelisted_users.append(user)

    context['list_of_whitelisted_users'] = list_of_whitelisted_users

    #POST
    if request.method == 'POST':
        #Add new blacklisted user
        whitelist_username = request.POST['whitelist-user']

        result = whitelist_user(loggedUser , whitelist_username)

        if result:
            messages.success(request, "Successfully whitelisted " + whitelist_username)
        else:
            messages.error(request, "This username exists in your whitelist.")

        return redirect('whitelist')

    else:
        
        return render(request, 'whitelist.html', context)

@login_required
def settings(request):
    
    if 'change-password' in request.POST:

        loggedUser = request.session.get('loggedin')
        old_password = request.POST['old-password']
        new_password = request.POST['new-password']
        confirm_new_password = request.POST['confirm-new-password']

        checkPassword = validate_login(loggedUser, old_password)

        if checkPassword:

            #check password
            if (new_password == confirm_new_password):
                result = change_password(loggedUser, new_password)

                if result:
                    messages.success(request,"You have successfully changed your password!")

                else:
                    messages.error(request, "There was an error changing your password.")

                return redirect('settings')

            else:
                messages.error(request, "The password confirmation does not match.")
                return redirect('settings')

        else:
            messages.error(request, "Invalid Password.")
            return redirect('settings')
    
    else:

        return render(request, 'settings.html', {})
