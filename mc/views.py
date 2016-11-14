from django.shortcuts import render
from django.http import HttpResponseRedirect

def index(request):
    return HttpResponseRedirect('/dashboard/')

def about(request):
    return render(request, 'pages/about.html')

def user_guide(request):
    return render(request, 'pages/user_guide.html')
