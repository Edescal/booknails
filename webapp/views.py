from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from . import models
from . import forms
import datetime

def index(request : WSGIRequest):
    cita = models.Cita()
    cita.fecha_cita = datetime.datetime.now()
    print(cita.fecha)
    print(cita.hora)
    print(cita.UNIX_timestamp)
    return render(request=request, template_name='index.html', context={})


def registro(request : WSGIRequest):    
    mensaje = ''
    if request.method == 'POST':
        form : forms.RegistroForm = forms.RegistroForm(request.POST)
        if form.is_valid():
            print('puta madre es valido')
            username = form.cleaned_data.get('usuario')
            email = form.cleaned_data.get('email')
            telefono = form.cleaned_data.get('telefono')
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirmar_password')
            nombre = form.cleaned_data.get('nombre', None)
            apellidos = form.cleaned_data.get('apellidos', None)

            if password == confirm_password:
                pass

            isinstance(models.Usuario, models.Usuario)

            usuario : models.Usuario = models.Usuario(
                username = username,
                email = email,
                telefono = telefono,
                password = password,
                nombre = nombre,
                apellidos = apellidos
            )
            mensaje = usuario
            pass
        else:
            print('errores')
            form.show_errors(request)
        
    elif request.method == 'GET':
        form : forms.RegistroForm = forms.RegistroForm()

    context = {
        'form': form,
        'mensaje': mensaje
    }
    return render(request=request, template_name='register.html', context=context)


def login(request : WSGIRequest):
    mensaje = ''
    if request.method == 'POST':
        form : forms.LoginForm = forms.LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            mensaje = str(user)
            """
            TODO: INICIO DE SESION EXITOSO
            """
        else:
            mensaje = 'Error de validacion'
            form.show_errors(request)

    elif request.method == 'GET':
        form : forms.LoginForm = forms.LoginForm()

    context = {
        'form': form,
        'mensaje': mensaje
    }
    return render(request=request, template_name='login.html', context=context)




