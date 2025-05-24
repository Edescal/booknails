from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.http.request import HttpRequest

from . import models, forms, services, utils
from api import serializers
import datetime


'''
=======================================
VISTAS PARA EL REGISTRO, LOGIN Y LOGOUT
=======================================
'''
def registro(request : HttpRequest):   
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = forms.RegistroForm(request.POST)
        if form.is_valid():
            apellidos = f"{form.cleaned_data['apellidos']}"
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
    if request.user.is_authenticated:
        return redirect('home')

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
                # verify = services.LoginVerify(usuario=user)
                # query_url = f'{reverse('auth_verify')}?token={utils.generar_token(verify.to_dict())}'
                # return redirect(query_url)

                login(request, user)

                print('Inicio de sesión exitoso')
                print(request.user.is_authenticated)
                request.session.save()
                return redirect('home')
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

def logout_view(request : HttpRequest):
    if request.user.is_authenticated:
        logout(request)
    return redirect(to='home', permanent=False)
'''
=======================================
'''
def success(request : HttpRequest):
    previous_url = request.META['HTTP_REFERER']
    print(f'Success from: {previous_url}')
    return render(request=request, template_name='success.html', context={ 'previous_url':previous_url })

@login_required
def editar_usuario(request : WSGIRequest):
    usuario = request.user
    if request.method == 'POST':
        form = forms.EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            # esto actualiza el modelo
            form.save()

            # Cambiar la contraseña solo si se ingresó una nueva
            nueva_contraseña = form.cleaned_data['password']
            if nueva_contraseña:
                if nueva_contraseña == form.cleaned_data['confirmar_password']:
                    usuario.set_password(nueva_contraseña)  # Encriptamos la nueva contraseña
                    usuario.save()  # Guardamos el usuario con la nueva contraseña
                else:
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return redirect('auth_editar_usuario')

            # Guardamos los cambios (si la contraseña no fue modificada, sólo los datos)
            usuario.save()
            messages.success(request, 'Tus datos han sido actualizados correctamente.')
            return redirect('auth_editar_usuario')  # Redirigir al perfil o la página que desees
    else:
        # Cargar los datos actuales del usuario para precargar el formulario
        form = forms.EditarUsuarioForm(instance=usuario)

    return render(request, 'editar_usuario.html', {'form': form})

@login_required
def ver_perfil(request : HttpRequest):

    return render(request, 'ver_perfil.html', {})


def verificar_login(request : HttpRequest):
    print(f'Usuario autenticado: {request.user.is_authenticated}')
    
    token = request.GET.get('token')
    if token:
        data, _ = utils.verificar_token(token, 43200)
        verify = services.LoginVerify(**data)
        print(f'Código de inicio: {verify.id}')
        print(f'Usuario identificado: {verify.usuario.get_full_name()}')
        if request.method == 'GET':
            '''AQUÍ MUESTRA EL FORMULARIO PARA PEDIR CÓDIGO DE VERIFICACIÓN'''
            print('Es GET')
        elif request.method == 'POST':
            '''AQUI RECUPERA DATOS DEL FORMULARIO PARA SABER SI EL CÓDIGO ES CORRECTO'''
            print('Es POST')
