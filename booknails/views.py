from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import datetime
from core import services

def index(request : WSGIRequest):
    
    if request.method == 'POST':
        dato = request.POST.get('mierda')
        hora = datetime.datetime.strptime(dato, '%H:%M:%S').time()
        print(hora)
        pass

    return render(request, 'index.html')



def menu(request : WSGIRequest):

    notificacion = services.Notificacion(request.user.email, 'sdsds', request.user)
    notificacion.enviar_confirmacion()

    return render(request, 'index.html')


def enviar_correo_electronico(usuario, username):
    asunto = 'Bienvenido a Booknails'
    contexto = {
        'usuario': usuario
    }
    html_content = render_to_string('emails/email_confirmation.html')


    pass