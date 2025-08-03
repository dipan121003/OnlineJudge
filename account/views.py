from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse


# Create your views here.
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = User.objects.filter(username=username, password=password)
        
        if user.exists():
            messages.info(request, 'User with this username already exists.')
            return redirect('/auth/register/')
        
        user = User.objects.create_user(username=username, password=password)
        user.set_password(password)  # Hash the password
        user.save()
        
        messages.info(request, 'User registered successfully.')
        return redirect('/auth/login/')
    
    template = loader.get_template('register.html')
    context = {}
    return HttpResponse(template.render(context,request))
        
def login_user(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.info(request,'User with this username does not exist')
            return redirect('/auth/login/')
        
        user = authenticate(username=username, password=password)

        if user is None:
            messages.info(request,'invalid password')
            return redirect('/auth/login')
        

        login(request,user)
        messages.info(request,'login successful')

        return redirect('/problems/list/')
    
    template = loader.get_template('login.html')
    context ={}
    return HttpResponse(template.render(context,request))   

def logout_user(request):
    logout(request)
    messages.info(request,'logout successful')
    return redirect('/auth/login/')