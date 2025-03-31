from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from core import models
import datetime, core.utils as utils

def index(request : WSGIRequest):


    return render(request, 'index.html')



def menu(request : WSGIRequest):

    return render(request, 'index.html')