from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.http import HttpResponse

def index(request : WSGIRequest):
    mensaje = rf"""
    <h1>Página de inicio</h1>
    <p>Si acabas de descargar este proyecto asegúrate de migrar la base de datos (MariaDB)</p>    
    <ol>
    <li>Crea una base de datos llamada 'booknails'</li>
    <li>Modifica las credenciales de usuario en 'settings.py' en la variable DATABASES</li>
    <li>Abre la terminal y ejecuta 'py manage.py makemigrations'</li>
    <li>Ejecuta 'py manage.py migrate'</li>
    <li>Si no te funciona, pregúntale a DeepSeek</li>
    </ol>
    { "\n".join([f'<li>{key}: {item}</li>' for key, item in request.META.items()]) }
    """
    return  HttpResponse(mensaje)

def menu(request : WSGIRequest):
    return render(request, 'index.html')