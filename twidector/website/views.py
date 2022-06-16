from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages

#from validate_email import validate_email
from mysql.connector.errors import IntegrityError
import pymysql.cursors

connection = pymysql.connect(host='db-mysql-sgp1-59801-do-user-11772463-0.b.db.ondigitalocean.com',
                             port=25060,
                             user='doadmin',
                             password='AVNS_8sOuFo_0JsSYDZDq3bL',
                             db='defaultdb',
                             cursorclass=pymysql.cursors.DictCursor)

# Create your views here.

def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        with connection.cursor() as cursor:
            sqlcommand = "SELECT `password` FROM `UserInfo` WHERE `username` = %s"
            cursor.execute(sqlcommand, (username))
        
            result = cursor.fetchone()
            print(result)
        
        if (result is None):
            messages.info(request, 'Invalid Username or password')
            return redirect('login')#goes back to login if wrong credentials

        elif (password == result["password"]):
            return redirect("register")    #goes to home page after successful login

        else:
            messages.info(request, 'Invalid Username or password')
            return redirect('login')#goes back to login if wrong credentials

    else:
        return render(request, 'login.html',{})

def register(request):
    return render(request, 'register.html', {})

def retrievepassword(request):
    return render(request, 'retrievepassword.html', {})

def freetrial(request):
    return render(request, 'freetrial.html', {})


