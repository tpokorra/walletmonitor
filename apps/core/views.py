from django.contrib.auth import authenticate
from django.shortcuts import render, redirect

def home(request):
    # if not logged in => redirect to login screen
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    # if logged in => redirect to monitor view
    return redirect('/monitor')
