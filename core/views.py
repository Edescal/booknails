from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
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
    print('MIERDOTA') 

    if request.method == 'POST':
        form = forms.RegistroForm(request.POST)
        if form.is_valid():
            apellidos = f'{form.cleaned_data['primer_apellido']} {form.cleaned_data['segundo_apellido']}'
            usuario = models.Usuario(
                username = form.cleaned_data['usuario'],
                email = form.cleaned_data['email'],
                telefono = form.cleaned_data['telefono'],
                password = form.cleaned_data['password'],
                nombre = form.cleaned_data['nombre'],
                apellidos = apellidos
            )
            usuario.save()
            messages.success(request, 'Registro exitoso', 'registro')
            return redirect('auth_success_view')
        else:
            form.show_errors(request)
    elif request.method == 'GET':
        form : forms.RegistroForm = forms.RegistroForm()
    context = { 'form': form }
    return render(request=request, template_name='register.html', context=context)


def login_view(request : WSGIRequest):
    print("ID de sesión:", request.session.session_key)
    mensaje = ''
    if request.method == 'POST':
        form : forms.LoginForm = forms.LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            # mensaje = str(user)

            # llama al authentication_backend para validar el usuario        
            user = authenticate(
                request, 
                username=user.username, 
                email = user.email, 
                password=form.cleaned_data['password']
            )
            if user:
                
                login(request, user)
                print('Inicio de sesión exitoso')
                print(request.user.is_authenticated)
                request.session.save()
                return redirect('auth_cita')
        else:
            # mensaje = 'Error de validacion'
            form.show_errors(request)

    elif request.method == 'GET':
        form : forms.LoginForm = forms.LoginForm()

    mensaje = str(request.user.is_authenticated)
    context = {
        'form': form,
        'mensaje': mensaje
    }
    return render(request=request, template_name='login.html', context=context)


def success(request : WSGIRequest):
    previous_url = request.META['HTTP_REFERER']
    print(f'Success from: {previous_url}')
    return render(request=request, template_name='success.html', context={ 'previous_url':previous_url })


@login_required
def agendar_cita(request : WSGIRequest):

    cliente = models.Usuario.objects.first()
    if request.method == 'POST':
        form = forms.CitasForm(cliente, request.POST)
        if form.is_valid():
            print('JEJE')
        else:
            print('ups')
            form.show_errors(request)
    elif request.method == 'GET':
        print(cliente)
        form : forms.CitasForm = forms.CitasForm(cliente=cliente)

    return render(request, 'cita.html', { 'form':form })

