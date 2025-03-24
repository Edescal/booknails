from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.http import HttpResponse

def index(request : WSGIRequest):
    
    return render(request, 'index.html')



def menu(request : WSGIRequest):

    return render(request, 'index.html')