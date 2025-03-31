from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.http import HttpResponse
from core import models
import datetime

def index(request : WSGIRequest):
    fecha = datetime.datetime.now().date()
    user = models.Usuario.objects.get(username='admin')
    cita = models.Cita.objects.filter(cliente=user, fecha_cita__date=fecha)
    print(cita)
    return render(request, 'index.html')



def menu(request : WSGIRequest):

    return render(request, 'index.html')