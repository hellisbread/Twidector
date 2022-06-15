from django.shortcuts import render

# Create your views here.

def login(request):
    return render(request, 'login.html',{})

def register(request):
    return render(request, 'register.html', {})

def retrievepassword(request):
    return render(request, 'retrievepassword.html', {})

def freetrial(request):
    return render(request, 'freetrial.html', {})