from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages

#from validate_email import validate_email
#from mysql.connector.errors import IntegrityError
from django.db import IntegrityError
import pymysql.cursors

connection = pymysql.connect(host='db-mysql-sgp1-59801-do-user-11772463-0.b.db.ondigitalocean.com',
                             port=25060,
                             user='doadmin',
                             password='AVNS_8sOuFo_0JsSYDZDq3bL',
                             db='defaultdb',
                             cursorclass=pymysql.cursors.DictCursor)

# Create your views here.
def index(request):
    return render(request,'index.html',{})

def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        with connection.cursor() as cursor:
            sqlcommand = "SELECT `epassword` FROM `UserInfo` WHERE `username` = %s"
            cursor.execute(sqlcommand, (username))
        
            result = cursor.fetchone()
            print(result)
        
        if (result is None):
            messages.info(request, 'Invalid Username or password')
            return redirect('login')#goes back to login if wrong credentials

        elif (password == result["epassword"]):
            return redirect("register")    #goes to home page after successful login

        else:
            messages.info(request, 'Error 2')
            return redirect('login')#goes back to login if wrong credentials

    else:
        return render(request, 'login.html',{})

def register(request):
    if request.method == 'POST' and 'username' in request.POST:
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        key = request.POST['key']
        usertype = request.POST['usertype']
        #resp = "Username already taken"

        with connection.cursor() as cursor:
            sqlcommand = "INSERT INTO `UserInfo` (`username`, `key`, `epassword`, `usertype`, `email`) VALUES (%s,%s,%s,%s,%s)"
            try:
                cursor.execute(sqlcommand, (username, key, password, usertype, email))
                connection.commit()
            except pymysql.IntegrityError:
                return("Username already taken")

            print('Details Updated')
            #return render(request,'login.html', {})
            result = cursor.fetchone() #to validate details

        if(result is None):
            #messages.info(request, 'Username already taken')
            return redirect('login') #goes to home page after successful registration
        
        elif(username == result["username"]):
            #return HttpResponse(resp)
            #return HttpResponse('Username already taken')
            messages.info(request, 'Username already taken')
            return redirect('register')    #goes back to login if wrong credentials
        
        else:
            messages.info(request, 'Error 2')
            return redirect('register')       #goes back to login if wrong credentials
    else:
        return render(request, 'register.html', {})

def forgotpassword(request):
    return render(request, 'forgot-password.html', {})

def resetpassword(request):
    return render(request, 'reset-password.html', {})

def freetrial(request):
    return render(request, 'free-trial.html', {})


