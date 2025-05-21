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

def crear_servicios():
    servicios = [
        (2, 'Acrílicas Tip', 330.00, 'M'),
        (3, 'Acrílicas Escultura', 350.00, 'M'),
        (4, 'Acrigel Top', 300.00, 'M'),
        (5, 'Soft Gel', 300.00, 'M'),
        (6, 'Nivelación con Rubber', 280.00, 'M'),
        (7, 'Kapping híbrido', 330.00, 'M'),
        (8, 'Gel semipermanente', 150.00, 'M'),
        (9, 'Manicura combinada', 250.00, 'M'),
        (10, 'Gel de construcción', 280.00, 'M'),
        (14, 'Acrílicas Tip', 360.00, 'F'),
        (15, 'Acrílicas Escultura', 380.00, 'F'),
        (16, 'Acrigel Tip', 340.00, 'F'),
        (17, 'Soft Gel', 340.00, 'F'),
        (18, 'Nivelación con Rubber', 330.00, 'F'),
        (19, 'Gel de construcción', 330.00, 'F'),
        (20, 'Kapping híbrido', 350.00, 'F'),
        (21, 'Pedicura tradicional', 300.00, 'P'),
        (22, 'Terapia con biogelly', 500.00, 'P'),
        (23, 'Pedicula spa', 600.00, 'P'),
        (24, 'Acripie', 300.00, 'P'),
        (25, 'Gel semipermanente', 130.00, 'P'),
        (26, 'Externo', 100.00, 'R'),
        (27, 'Salón', 80.00, 'R'),
    ]
    for id_, nombre, precio, categoria in servicios:
        servicio, creado = models.Servicio.objects.update_or_create(
            id=id_,
            defaults={
                'nombre': nombre,
                'precio': precio,
                'categoria': categoria
            }
        )
        print(f"{'Creado' if creado else 'Actualizado'}: {servicio}")


def index(request : WSGIRequest):
    if models.Usuario.objects.count() == 0:
        print('No hay usuarios activos')
        crear_admin()
        try:
            crear_servicios()
        except:
            print('WHAT')
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

