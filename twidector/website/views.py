from wsgiref import validate
from django.shortcuts import render, redirect
from django.contrib import messages

from website.functions import *

# Create your views here.
def index(request):
    return render(request,'index.html',{})

def aboutUs(request):
    return render(request,'about-us.html',{})

def aboutTeam(request):
    return render(request,'about-team.html',{})

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
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            usertype = 0

            result = register_user(username, password, usertype, email)

            if result:
                messages.success(request, 'Successfully Created Account')
                return redirect('login')
            else:
                messages.error(request, 'This username may already exist.')
                return redirect('register')
            
        else:
            return render(request, 'register.html', {})
    else:
        return redirect('index')


def forgotPassword(request):
    return render(request, 'forgot-password.html', {})

def resetPassword(request):
    return render(request, 'reset-password.html', {})

def freeTrial(request):
    return render(request, 'free-trial.html', {})

def freeTrialTwo(request):
    return render(request, 'free-trial-2.html', {})




#Dashboard Views

def dashboard(request):
    return render(request, 'dashboard.html', {})

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

            


        


