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

def index(request : WSGIRequest):

    return render(request=request, template_name='index.html')

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
def editar_usuario(request : WSGIRequest):
    usuario = request.user
    if request.method == 'POST':
        form = forms.EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            # Cambiar la contraseña solo si se ingresó una nueva
            nueva_contraseña = form.cleaned_data['password']
            if nueva_contraseña:
                if nueva_contraseña == form.cleaned_data['confirmar_password']:
                    usuario.set_password(nueva_contraseña)  # Encriptamos la nueva contraseña
                    usuario.save()  # Guardamos el usuario con la nueva contraseña
                else:
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return redirect('editar_usuario')

            # Guardamos los cambios (si la contraseña no fue modificada, sólo los datos)
            usuario.save()
            messages.success(request, 'Tus datos han sido actualizados correctamente.')
            return redirect('auth_index')  # Redirigir al perfil o la página que desees
    else:
        # Cargar los datos actuales del usuario para precargar el formulario
        form = forms.EditarUsuarioForm(instance=usuario)

    return render(request, 'editar_usuario.html', {'form': form})


@login_required
def agendar_cita(request : HttpRequest):

    cliente = models.Usuario.objects.first()
    if request.method == 'POST':
        form = forms.CitasForm(cliente, request.POST)
        '''
        VALIDAR FORMULARIO
        '''
        if form.is_valid():
            print('JEJE')

            cita = form.to_cita()
            if cita:
                print('================')
                print(f'Nueva cita creada: {cita.id}')
                print('================')
                return redirect('auth_success_view')
        else:
            print('ups')
            form.show_errors(request)

    elif request.method == 'GET':
        """
        MOSTRAR FORMULARIO
        """
        form : forms.CitasForm = forms.CitasForm(cliente=cliente)
        form.fields['servicios'].queryset = models.Servicio.objects.none()


    return render(request, 'cita.html', { 'form':form })


def verificar_token(request):

    return HttpResponse('SSDSDSD')
