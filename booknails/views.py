from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import datetime, logging
from core import services, models


def crear_admin():
    user, new_instance = models.Usuario.objects.get_or_create(
        username = 'admin'
    )
    if new_instance:
        user.is_superuser = True
        user.username = 'admin'
        user.nombre = 'Katty Caridad'
        user.apellidos = 'Magariño Marín'
        user.email = 'eduardo1582000@gmail.com'
        user.fecha_creacion = datetime.datetime.now()
        user.telefono = '9993914295'
        user.set_password('password')
        user.save()


def index(request : WSGIRequest):
    if models.Usuario.objects.count() == 0:
        print('No hay usuarios activos')
        crear_admin()
    return render(request, 'index.html')



def menu(request : WSGIRequest):

    cita = models.Cita.objects.filter(cliente=request.user).first()
    print(cita)

    notificacion = services.Notificacion(request.user)
    print(notificacion)
    return HttpResponse(notificacion._render_email({
        'usuario':request.user,
        'cita':cita
    }))
    # if notificacion.enviar_confirmacion():
    #     logging.info('Se envió un correo exitosamente')
    # else:
    #     logging.error('No se envió el correo')

    return render(request, 'index.html')

