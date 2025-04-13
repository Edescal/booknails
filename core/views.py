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
                # verify = services.LoginVerify(usuario=user)
                # query_url = f'{reverse('auth_verify')}?token={utils.generar_token(verify.to_dict())}'
                # return redirect(query_url)

                login(request, user)
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


@login_required
def recuperar_citas(request : HttpRequest):

    mes = datetime.datetime.now().date().month
    citas = models.Cita.objects.filter(fecha_cita__month=mes)   
    citas = citas.order_by('fecha_cita')
        
    print('---------------------')
    for c in citas:
        servicios : list[models.Servicio] = c.servicios.all()
        for s in servicios:
            print(f'{s.nombre} Precio: ${s.precio}')

    context = {
        'citas': citas
    }
    return render(request=request, template_name='citas_registradas.html', context=context)



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


    return HttpResponse(str(data))
