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
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm, SetPasswordForm
from django.contrib.messages.views import SuccessMessageMixin

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

#from website.models import CustomTwidectorUser

from .forms import user_info

from .forms import UserRegistrationForm
from django.contrib.auth import views as auth_views
from django.contrib.admin.views.decorators import staff_member_required

from .tokens import account_activation_token
from django.contrib.auth.tokens import default_token_generator

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
#from django.utils import six
#from django.contrib.auth import login, authenticate
from django.core.mail import send_mail, BadHeaderError

from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.models import User
user = get_user_model()
from .models import TwitterAuthToken, TwitterUser, SyncTwitterAccount, Blocked, Favourited , Tweet

from website.functions import *
from website.hatedetection import *
from website.relationshipScore import *
from website.graphs import *
from website.maintenance import *
from website.twitter_api import TwitterAPI
from website.authorization import create_update_user_from_twitter, check_token_still_valid
from django.db.models import Q

import time



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
    #prepareDF()
    #df = sql_to_dataframe_hate()
    new_hate_data()
    #retrain()

    #print(df)
    return render(request,'index.html',{})

def aboutUs(request):
    return render(request,'about-us.html',{})

def aboutTeam(request):
    return render(request,'about-team.html',{})

def freeTrial(request):

    context = {}

    if request.method == 'POST':

        url = request.POST['twitter-url']

        #prepareDF()
        try:
            twitterID = getuserid(url)
        except:
            messages.error(request, 'Invalid Twitter User Handle. Please key in a valid twitter user.')

            return render(request, 'free-trial.html', context)
        twitterIMGURL = getuserIMG(twitterID)

        data = getalltweets(twitterID, 200)

        predicted_score = predictHate(data['tweet'])
        data['predicted_score'] = predicted_score  
        data['userID'] = twitterID

        typeCount = getTweetTypeCount(data)

        context = {'dataframe': data , 'user' : url, 'img' : twitterIMGURL, 'TypeCount' : typeCount}

        print(context)

        return render(request, 'free-trial.html', context)
    else:
        return render(request, 'free-trial.html', context)

#Login/Register Views
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

            if form.is_valid():
                user = get_user_model()
                user = form.save(commit=False)
                user.is_active = False
                user.save()  
                current_site = get_current_site(request)
                subject = "Twidector Account Activation"
                message = render_to_string('activate_account_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':account_activation_token.make_token(user),
                'protocol': request.scheme,
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
        time.sleep(2)
        return redirect('login')
    else:
        messages.error(request, 'Activation link invalid.')
        return redirect('login')

def forgotPassword(request):

    return render(request, 'forgot-password.html', {})


def password_reset_form(request):

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        #form = auth_views.PasswordResetView(request.POST)
        email = request.POST.get('email')
        
        if form.is_valid():
            user = User.objects.filter(email=email).first()
            if user is not None:
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
                'token':default_token_generator.make_token(user),
                'protocol': request.scheme,
            })
                try:
                    send_mail(subject, message, 'twidector@gmail.com' , [user.email], fail_silently=False, html_message=message)
                    # messages.success(request, 'Successfully sent to email on how to reset password')
                    # return redirect('login')
                except:
                    return HttpResponse('Invalid header found.')
                return redirect ("/password_reset_done/")

    form = PasswordResetForm()
    #form = auth_views.PasswordResetView()

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
            form = SetPasswordForm(request.user, request.POST)
            if form.is_valid():
                update_session_auth_hash(request, user)
                new_password = request.get('new_password1')
                user.set_password(new_password)
                user.save()
                form.save()
                messages.success(request,"You have successfully changed your password!")
                return redirect('login')

            else:
                messages.error(request,"You have failed to changed your password!")
                return redirect('login')
                

    else:
        messages.error(request, 'Reset link invalid.')
        return redirect('login')

    form = SetPasswordForm(request.user)

    return render(request, 'password_reset_confirm.html', {'form': form})





#def resetPassword(request):
    return render(request, 'reset-password.html', {})

#def forgotUsername(request):
    return render(request, 'forgot-password.html', {})
    
def login_twitter(request):
    twitter_api = TwitterAPI()
    url, oauth_token, oauth_token_secret = twitter_api.twitter_login()
    if url is None or url == '':
        messages.error(request, 'Error.')
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


def login_twitter_callback(request):
    if 'denied' in request.GET:
        messages.error(request, 'Error.')
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
                messages.error(request, 'Error.')
                return redirect('index')
        else:
            messages.error(request, 'Error.')
            return redirect('index')
    else:
        messages.error(request, 'Error.')
        return redirect('index')

def sync_twitter(request):
    twitter_api = TwitterAPI()
    url, oauth_token, oauth_token_secret = twitter_api.twitter_sync()
    if url is None or url == '':
        messages.error(request,'Error.')
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

def sync_twitter_callback(request):
    if 'denied' in request.GET:
        messages.error(request,'Error.')
        return redirect('index')

    sync_account = SyncTwitterAccount.objects.filter(user_id=request.user.id).first()

    if sync_account is None:
        twitter_api = TwitterAPI()
        oauth_verifier = request.GET.get('oauth_verifier')
        oauth_token = request.GET.get('oauth_token')
        twitter_auth_token = TwitterAuthToken.objects.filter(oauth_token=oauth_token).first()
        if twitter_auth_token is not None:
            access_token, access_token_secret = twitter_api.twitter_callback_sync(oauth_verifier, oauth_token, twitter_auth_token.oauth_token_secret)
            if access_token is not None and access_token_secret is not None:
                twitter_auth_token.oauth_token = access_token
                twitter_auth_token.oauth_token_secret = access_token_secret
                twitter_auth_token.save()
                info = twitter_api.get_me(access_token, access_token_secret)
                if info is not None:
                    twitter_user_new = TwitterUser(twitter_id=info[0]['id'], screen_name=info[0]['username'])
                    twitter_user_new.twitter_oauth_token = twitter_auth_token
                    user, twitter_user_new = create_update_user_from_twitter(twitter_user_new)

                    #sync_account = SyncTwitterAccount.objects.filter(twitter_id=info[0]['id']).first()

                    sync_pair = SyncTwitterAccount(user_id=request.user.id, twitter_id=info[0]['id'])
                    sync_pair.save()

                    return redirect('settings')

                else:
                    messages.error(request,'Error.')
                    return redirect('index')
            else:
                messages.error(request,'Error.')
                return redirect('index')
        else:
            messages.error(request,'Error.')
            return redirect('index')
    else:
        sync_account.delete()
        return redirect('settings')


def deactivate_account(request):
    return render(request, 'deactivate_account.html')

def deactivate_account_true(request):
    user = request.user
    user.is_active = False
    user.save()
    auth_logout(request)
    messages.success(request, 'Successfully deactivated account. If you would like to reactivate your account, submit a password reset request on the login page.')
    return redirect('index')

def deactivate_account_false(request):

    return redirect('settings')

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

#showing the accuracy score 
def accuracyScore(request):
    value = prepareDF()
    graph_interpretation = graph_values()
    return render(request, 'accuracy-score.html', {'value': value , 'graph_interpretation': graph_interpretation})


def ascore_fakenews(request):
    fn_val = train_FN_Model()
    g_fn = fn_graph()
    return render(request, 'ascore-fn.html', {'fn_val' : fn_val , 'g_fn' : g_fn})

def drop_file(request):
    if request.method == "POST":
    # do the reading inside here (the checking, the reading)

        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'This is not a csv file!')
            return redirect('ascore-fn')
        v = scores(csv_file)
        fn_val = train_FN_Model()
        g_fn = fn_graph()

        return render(request, 'ascore-fn.html',{'fn_val' : fn_val , 'g_fn' : g_fn ,'v' : v} )

def file_upload(request):
    if request.method == "POST":
    # do the reading inside here (the checking, the reading)

        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'This is not a csv file!')
            return redirect('accuracy-score')

        result = uploadScoring(csv_file)
        value = prepareDF()
        graph_interpretation = graph_values()

        return render(request, 'accuracy-score.html', {'result': result, 'value': value ,'graph_interpretation': graph_interpretation})

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
    display_graph = get_graph()
    fn_gr = fakenews_graph()
    return render(request, 'model-testing.html', {'display_graph': display_graph ,'fn_gr' : fn_gr})

def reportedTweets(request):
    #returning the reported tweets
    tweet_t = Tweet.objects.filter(flagged = 1).values()
 
    return render(request, 'reported-tweets.html', {'tweet_t': tweet_t})

def accessing_score(request):
    tweet_t = Tweet.objects.filter(flagged = 1).values()

    if 'request_id' in request.POST:
     #getting the id of each button which is the tweet id
       t_id = request.POST.get('request_id')
     #getting the grading option ( 0 , 1 , 2)
       grading_option = request.POST.get('inlineRadioOptions')
     #button 
       if 'grade' in request.POST:
         tweet_score(t_id , grading_option)

    context = {'tweet_t' : tweet_t}

    context.update()

    return render(request, 'reported-tweets.html', {'tweet_t': tweet_t})

#Dashboard Views
@login_required
#@twitter_login_required
def dashboard(request):
    context = {'twitter_id_exist':True}

    user_id = request.user.id

    try: #Get from sync
        print("twitter id attempt")
        twitter_sync_obj = SyncTwitterAccount.objects.get(user = user_id)
        twitter_id = twitter_sync_obj.twitter_id

        twitter_user_obj = TwitterUser.objects.get(twitter_id = twitter_id)
        access_token_info = TwitterUser.objects.select_related('twitter_oauth_token').get(id = twitter_user_obj.id)
        

    except: #Get from twitter user

        try:
            twitter_obj = TwitterUser.objects.get(user = user_id)
            twitter_id = twitter_obj.twitter_id

            access_token_info = TwitterUser.objects.select_related('twitter_oauth_token').get(id = twitter_obj.id)

        except:
            return render(request, 'dashboard.html', {'twitter-id-exist':False})

    updateAccess(access_token_info.twitter_oauth_token.oauth_token, access_token_info.twitter_oauth_token.oauth_token_secret)

    if 'dashboard-info' in request.session:
        context = request.session.get('dashboard-info')
        del request.session['dashboard-info']

        return render(request, 'dashboard.html', context)

    else:

        twitter_handle = getuserUserHandle(twitter_id)

        relationship = assess_relationship(twitter_handle)

        relationship_list = retrieve_top_users(relationship, 6, request.user)

        print(relationship_list)

        context.update({'relationship_access':relationship_list})

        request.session['dashboard-info'] = context

        return render(request, 'dashboard.html', context)

@login_required
def analyse(request):

    if 'search-url' in request.POST:

        if 'current-search' in request.session:
            del request.session['current-search']

        url = request.POST["twitter-url"]

        #prepareDF()

        twitterID = getuserid(url)

        twitterIMGURL = getuserIMG(twitterID)

        data = getalltweets(twitterID, 1000)

        print(data)

        predicted_score = predictHate(data['tweet'])
        data['predicted_score'] = predicted_score  
        data['userID'] = twitterID

        typeCount = getTweetTypeCount(data)

        dataSize = data.shape[0]

        context = {'dataframe': data ,'dataSize': dataSize, 'user' : url, 'img' : twitterIMGURL, 'TypeCount' : typeCount}

        transfer = {'dataframe': data.to_json() ,'dataSize':int(dataSize), 'user' : url, 'img' : twitterIMGURL, 'TypeCount' : typeCount}

        request.session['current-search'] = transfer

        return render(request, 'analyse.html', context)

    elif 'filter' in request.POST:

        context = request.session.get('current-search')

        filterOption = request.POST['filter-by']

        if(filterOption=='Choose...'):

            data = {'dataframe': pd.read_json(context.get('dataframe'))}

            context.update(data)

            return render(request, 'analyse.html', context) 

        data = pd.read_json(context.get('dataframe'))

        filtered_data = {'dataframe': data[data['predicted_score']==int(filterOption)]}

        context.update(filtered_data)
       
        return render(request, 'analyse.html', context) 
    else:
        if 'current-search' in request.session:
            del request.session['current-search']

        return render(request, 'analyse.html', {})

@login_required
def reportTweets(request, tweet_id):

    context = request.session.get('current-search')

    data = {'dataframe': pd.read_json(context.get('dataframe'))}

    context.update(data)

    print(tweet_id)

    return render(request, 'analyse.html', context) 

@login_required
def viewTweet(request):
    return render(request, 'view-tweet.html', {})

@login_required
def blocklist(request):

    context = {}

    if 'add-block' in request.POST:

        twitter_handle = request.POST['blacklist-user']

        try:
            twitter_id = getuserid(twitter_handle)
        except:
            messages.error(request, 'Invalid Twitter User')
            return redirect('block-list')

        new_block_user = Blocked(
                            blocked_twitter_id = twitter_id,
                            blocked_username = twitter_handle,
                            user = request.user,
                            soft_delete = 0
                            )

        new_block_user.save()

        messages.success(request, "Successfully added " + twitter_handle + " to block list.")

        return redirect('block-list')

    blocked_objectlist = Blocked.objects.filter(user = request.user).filter(soft_delete=0).values_list('blocked_twitter_id', 'blocked_username')

    print(blocked_objectlist)

    context = {'blocked_list': blocked_objectlist}

    return render(request, 'blacklist.html', context)

@login_required
def add_blocklist(request, user_id):
    twitter_handle = user_id

    try:
        twitter_id = getuserid(twitter_handle)
    except:
        messages.error(request, 'Invalid Twitter User')
        return redirect('block-list')

    new_block_user = Blocked(
                        blocked_twitter_id = twitter_id,
                        blocked_username = twitter_handle,
                        user = request.user,
                        soft_delete = 0
                        )

    new_block_user.save()

    messages.success(request, "Successfully added " + twitter_handle + " to block list.")

    return redirect('dashboard')

@login_required
def delete_blocklist(request, user_id):

    twitter_handle = user_id

    try:
        twitter_id = getuserid(twitter_handle)
    except:
        messages.error(request, 'Invalid Twitter User')
        return redirect('favourites')

    update_block_user = Blocked.objects.get(blocked_twitter_id = twitter_id)

    update_block_user.soft_delete = 1

    update_block_user.save()

    messages.success(request, "Successfully removed " + twitter_handle + " from the block list.")

    return redirect('block-list')

@login_required
def favouritelist(request):

    context = {}

    if 'add-favourite' in request.POST:

        twitter_handle = request.POST['favourite-user']

        try:
            twitter_id = getuserid(twitter_handle)
        except:
            messages.error(request, 'Invalid Twitter User')
            return redirect('favourites')

        new_favourite_user = Favourited(
                            favourited_twitter_id = twitter_id,
                            favourited_username = twitter_handle,
                            user = request.user,
                            soft_delete = 0
                            )

        new_favourite_user.save()

        messages.success(request, "Successfully added " + twitter_handle + " to favourites.")

        return redirect('favourites')

    favourited_objectlist = Favourited.objects.filter(user = request.user).filter(soft_delete=0).values_list('favourited_twitter_id', 'favourited_username')

    print(favourited_objectlist)

    context = {'favourites_list': favourited_objectlist}

    return render(request, 'whitelist.html', context)

@login_required
def add_favouritelist(request, user_id):

    twitter_handle = user_id

    try:
        twitter_id = getuserid(twitter_handle)
    except:
        messages.error(request, 'Invalid Twitter User')
        return redirect('favourites')

    new_favourite_user = Favourited(
                        favourited_twitter_id = twitter_id,
                        favourited_username = twitter_handle,
                        user = request.user,
                        soft_delete = 0
                        )

    new_favourite_user.save()

    messages.success(request, "Successfully added " + twitter_handle + " to favourites.")

    return redirect('dashboard')

@login_required
def delete_favouritelist(request, user_id):

    twitter_handle = user_id

    try:
        twitter_id = getuserid(twitter_handle)
    except:
        messages.error(request, 'Invalid Twitter User')
        return redirect('favourites')

    update_favourite = Favourited.objects.get(favourited_twitter_id = twitter_id)

    update_favourite.soft_delete = 1

    update_favourite.save()

    messages.success(request, "Successfully removed " + twitter_handle + " from favourites.")

    return redirect('favourites')

# @login_required
def settings(request):
    
    if 'change-password' in request.POST:
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            #user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request,"You have successfully changed your password!")

        else:
            messages.error(request, "There was an error changing your password.")

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'settings.html', {'form': form})
