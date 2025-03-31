from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.http.request import HttpRequest

from . import models, forms, services, utils
import datetime

def crear_admin():
    user = models.Usuario()
    user.is_superuser = True
    user.username = 'admin'
    user.nombre = 'Eduardo'
    user.apellidos = 'Escalante Pacheco'
    user.email = 'eduardo1582000@gmail.com'
    user.fecha_creacion = datetime.datetime.now()
    user.telefono = '9993914295'
    user.set_password('password')
    user.save()







'''
=======================================
VISTAS PARA EL REGISTRO, LOGIN Y LOGOUT
=======================================
'''
def registro(request : HttpRequest):   
    if request.method == 'POST':
        form = forms.RegistroForm(request.POST)
        if form.is_valid():
            apellidos = f'{form.cleaned_data['primer_apellido']} {form.cleaned_data['segundo_apellido']}'
            usuario = models.Usuario(
                username = form.cleaned_data['usuario'],
                email = form.cleaned_data['email'],
                telefono = form.cleaned_data['telefono'],
                nombre = form.cleaned_data['nombre'],
                apellidos = apellidos
            )
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            messages.success(request, 'Registro exitoso', 'registro')
            return redirect('auth_success_view')
        else:
            form.show_errors(request)
    elif request.method == 'GET':
        form : forms.RegistroForm = forms.RegistroForm()
    context = { 'form': form }
    return render(request=request, template_name='register.html', context=context)


def login_view(request : HttpRequest):
    print("ID de sesión:", request.session.session_key)
    mensaje = ''
    if request.method == 'POST':
        form : forms.LoginForm = forms.LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()

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

@login_required
def logout_view(request : HttpRequest):
    if request.user.is_authenticated:
        logout(request)
    return redirect(to='auth_login', permanent=False)
'''
=======================================
'''
def success(request : HttpRequest):
    previous_url = request.META['HTTP_REFERER']
    print(f'Success from: {previous_url}')
    return render(request=request, template_name='success.html', context={ 'previous_url':previous_url })


@login_required
def agendar_cita(request : HttpRequest):
    cliente = request.user
    if request.method == 'POST':
        form = forms.CitasForm(cliente, request.POST)
        if form.is_valid():
            cita = form.to_cita()
            if cita:
                print(f'Nueva cita creada: {cita.id}')
                return redirect('auth_success_view')
        else:
            form.show_errors(request)
    elif request.method == 'GET':
        form : forms.CitasForm = forms.CitasForm(cliente=cliente)
        
    form.fields['servicios'].queryset = models.Servicio.objects.none()
    return render(request, 'cita.html', { 'form':form })




def verificar_token(request):

    return HttpResponse('SSDSDSD')
