from django.shortcuts import render
from app.forms import *
from django.http import HttpResponse,HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.
import requests
def home(request):
    if request.session.get('username'):
        username = request.session.get('username')
        d = {'username': username}
        return render(request, 'home.html', d)
    return render(request, 'home.html')
def registration(request):
    uf = UserForm()
    pf = ProfileForm()
    d = {'uf': uf, 'pf': pf}
    
    if request.method == 'POST' and request.FILES:
        UFD = UserForm(request.POST)
        PFD = ProfileForm(request.POST, request.FILES)
        if UFD.is_valid() and PFD.is_valid():
            UFO = UFD.save(commit=False)
            password = UFD.cleaned_data['password']
            UFO.set_password(password)
            UFO.save()
            
            PFO = PFD.save(commit=False)
            PFO.profile_user = UFO
            PFO.save()
            
            send_mail('registration',
                      'Thanks for registration,ur registration is successful',
                      'sandhyabehera33090@gmail.com',
                      [UFO.email],
                      fail_silently=False)
            return HttpResponseRedirect('registration is successful')
    return render(request, 'registration.html', d)

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('un')
        password = request.POST.get('pw')
        user = authenticate(username=username, password=password)
        
        if user and user.is_active:
            login(request, user)
            request.session['username'] = username
            return HttpResponseRedirect(reverse('home'))
        else:
            return HttpResponse("U are not an authenticated user")
    
    return render(request, 'user_login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

@login_required
def profile_display(request):
    un = request.session.get('username')
    UO = User.objects.get(username=un)
    PO = Profile.objects.get(profile_user=UO)

    d = {'UO': UO, 'PO': PO}
    return render(request, 'profile_display.html', d)

@login_required
def change_password(request):
    if request.method == 'POST':
        pw = request.POST['password']
        un = request.session.get('username')
        UO = User.objects.get(username=un)
        UO.set_password(pw)
        UO.save()
        return HttpResponseRedirect('password changed successfully')
    return render(request, 'change_password.html')

def reset_password(request):
    if request.method == 'POST':
        un = request.POST['un']
        pw = request.POST['pw']
        LUO = User.objects.filter(username=un)
        if LUO :
            UO = LUO[0]
            UO.set_password(pw)
            UO.save()
            return HttpResponseRedirect('password reset successfully')
        else:
            return HttpResponse('user not found')
        return HttpResponse('Reset password is done successfully')
    return render(request, 'reset_password.html')

@login_required
def search(request):
    if request.method == 'POST':
        city_name = request.POST['city']
        api_key = 'a0c2f3b8d1e4f5b7c6e9d4f5a0e4f5b7'
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}'
        response = requests.get(url)
        Weather_data = response.json()
        print(Weather_data)
        tempature = Weather_data['main']['temp']
        humidity = Weather_data['main']['humidity']
        weather = Weather_data['main']['feels_like']
        speed = Weather_data['wind']['speed']
        username = request.session.get('username')
        LUO = User.objects.get(username=username)
        obj = WeatherData.objects.get_or_create(username=LUO, city=city_name, temperature=tempature, humidity=humidity, weather=weather, speed=speed)[0]
        obj.save()
        d = {'obj':obj}
        return render(request, 'search.html', d)
    return render(request, 'search.html')

@login_required
def user_history(request):
    username = request.session.get('username')
    UO = User.objects.get(username=username)
    LWO = WeatherData.objects.filter(username=UO)
    d = {'LWO': LWO}
    return render(request, 'user_history.html', d)

def all_history(request):
    LWO = WeatherData.objects.all()
    d = {'LWO': LWO}
    return render(request, 'all_history.html', d)
        