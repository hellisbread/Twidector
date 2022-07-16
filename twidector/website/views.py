#import git
from wsgiref import validate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import UserRegistrationForm

from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils import six
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

from django.contrib.auth import get_user_model

from website.functions import *

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
    return render(request, 'free-trial.html', {})

def freeTrialTwo(request):
    return render(request, 'free-trial-2.html', {})

#Login/Register Views

def login(request):
    if 'loggedin' not in request.session:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            result = validate_login(username, password)

            if result:
                messages.success(request, 'Successfully Login to Account')

                request.session['loggedin'] = username
                return redirect('dashboard')
                
            else:
                messages.error(request, 'Invalid Username or Password')
                return redirect('login')

        else:
            return render(request, 'login.html', {})
    else:
        return redirect('index')

def logout(request):
    if 'loggedin' not in request.session:

        return redirect('login')

    else:
        del request.session['loggedin']
        messages.success(request, 'Successfully Logged out.')
        return redirect('login')
        
def register(request):

    if 'loggedin' not in request.session:
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password1')
            passwordcheck = request.POST.get('password2')
            usertype = 0

            if(password != passwordcheck):
                messages.error(request, 'Error. Password does not match.')
                return redirect('register')

            if form.is_valid():

                result = register_user(username, password, usertype, email)

                if result:
                    user = form.save(commit=False)  
                    user.save()  
                    current_site = get_current_site(request)
                    message = render_to_string('acc_activate_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                    'token':account_activation_token.make_token(user),  
                })
                    send_registration_email(email, message)
                    messages.success(request, 'Successfully Created Account')
                    return redirect('login')
                else:
                    messages.error(request, 'This username may already exist.')
                    return redirect('register')

        else:
            form = UserRegistrationForm()

        return render(request, 'register.html', {'form':form})
            
    else:
        return redirect('index')

def activate(request, uidb64, token):
    User = get_user_model()  
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
        
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.save()
        activate_user(user.username)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. You can now login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

def forgotPassword(request):
    return render(request, 'forgot-password.html', {})

def resetPassword(request):
    return render(request, 'reset-password.html', {})

#Admin Views

def adminLogin(request):
    if 'adminlog' not in request.session:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            result = validate_login(username, password)

            if result:
                messages.success(request, 'Successfully Login to Admin Panel')

                request.session['adminlog'] = username
                return redirect('admin/home')
                
            else:
                messages.error(request, 'Invalid Username or Password')
                return redirect('admin')

        else:
            return render(request, 'admin-login.html', {})
    else:
        return redirect('index')

def accuracyScore(request):
    return render(request, 'accuracy-score.html', {})

def adminPage(request):
    return render(request, 'admin-page.html', {})

def searchAccount(request):
    return render(request, 'search-account.html', {})

def updateUser(request):
    return render(request, 'update-user.html', {})

#Dashboard Views

def dashboard(request):
    if 'loggedin' not in request.session:
        messages.error(request, 'please login before enterring the dashboard.')
        return redirect('login')

    else:
        return render(request, 'dashboard.html', {})

def analyse(request):
    if 'loggedin' not in request.session:
        messages.error(request, 'please login before enterring the dashboard.')
        return redirect('login')

    else:
        return render(request, 'analyse.html', {})

def analyseTwo(request):
    if 'loggedin' not in request.session:
        messages.error(request, 'please login before enterring the dashboard.')
        return redirect('login')

    else:
        return render(request, 'analyse-2.html', {})

def viewTweet(request):
    if 'loggedin' not in request.session:
        messages.error(request, 'please login before enterring the dashboard.')
        return redirect('login')

    else:
        return render(request, 'view-tweet.html', {})

def blacklist(request):

    if 'loggedin' not in request.session:
        messages.error(request, 'please login before enterring the dashboard.')
        return redirect('login')

    else:
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

def whitelist(request):

    if 'loggedin' not in request.session:
        messages.error(request, 'please login before enterring the dashboard.')
        return redirect('login')
    else:
        context = {}

        loggedUser = request.session.get('loggedin')

        #Retrieve List
        whitelisted_users = retrieve_whitelist(loggedUser)

        #Convert List to context dict
        list_of_whitelisted_users = []
        for user in whitelisted_users:
            list_of_whitelisted_users.append(user)

        context['list_of_whitelisted_users'] = list_of_whitelisted_users

        print(context)

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

def settings(request):
    if 'loggedin' not in request.session:
        messages.error(request, 'please login before enterring the dashboard.')
        return redirect('login')
    else:

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

            


        


