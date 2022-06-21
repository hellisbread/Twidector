from wsgiref import validate
from django.shortcuts import render
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
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        result = validate_login(username, password)

        if result:
            messages.success(request, 'Successfully Login to Account')

            request.session['loggedin'] = username
            return redirect('login')
        else:
            messages.error(request, 'Invalid Username or Password')
            return redirect('login')

    else:
        return render(request, 'login.html',{})

def logout(request):
    if 'loggedin' not in request.session:

        return redirect('login')

    else:
        del request.session['loggedin']
        messages.success(request, 'Successfully Logged out.')
        return redirect('index')
        
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        twitterusername = request.POST['twitterusername']
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


def forgotPassword(request):
    return render(request, 'forgot-password.html', {})

def resetPassword(request):
    return render(request, 'reset-password.html', {})

def freeTrial(request):
    return render(request, 'free-trial.html', {})


