from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required

from rest_framework.response import Response
from rest_framework.decorators import api_view

from . import models, forms, serializers
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
    today = datetime.datetime.today().date() + datetime.timedelta(days=6)
    instance, created = models.FechaBloqueada.objects.get_or_create(fecha=today)
    if created:
        print(f'Nueva {instance}')
    else:
        print(instance)

    if models.Usuario.objects.count() == 0:
        crear_admin()
        print('Admin creado')

    if models.Cita.objects.count() == 0:
        cita = models.Cita()
        cita.fecha_cita = datetime.datetime.now()
        cita.fecha_creacion = datetime.datetime.now()
        cita.id_cliente = models.Usuario.objects.first()
        cita.id_servicio = models.Servicio.objects.first()
        cita.save()

    citas = models.Cita.objects.all()
    for cita in citas:
        print('=======================')
        print(cita)
        print(cita.fecha)
        print(cita.hora)
        print(cita.UNIX_timestamp)
    return render(request=request, template_name='index.html', context={ 'citas':citas })

'''
=======================================
VISTAS PARA EL REGISTRO, LOGIN Y LOGOUT
=======================================
'''
def registro(request : WSGIRequest):   
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


def login_view(request : WSGIRequest):
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
def logout_view(request : WSGIRequest):
    if request.user.is_authenticated:
        logout(request)
    return redirect(to='auth_login', permanent=False)
'''
=======================================
'''
def success(request : WSGIRequest):
    previous_url = request.META['HTTP_REFERER']
    print(f'Success from: {previous_url}')
    return render(request=request, template_name='success.html', context={ 'previous_url':previous_url })


@login_required
def agendar_cita(request : WSGIRequest):

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
                print('Nueva cita registrada')
                cita.save()
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

    return render(request, 'cita.html', { 'form':form })


"""
====================================
MÉTODOS PARA LAS APIS DE LOS MODELOS
====================================
"""
# region APIS
@api_view(['GET'])
def api_get_citas(request):
    citas = models.Cita.objects.all()
    serializer = serializers.CitaSerializer(citas, many=True)
    return Response(serializer.data)
    
@api_view(['GET'])
def api_get_usuarios(request):
    usuarios = models.Usuario.objects.all()
    serializer = serializers.UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_get_servicios(request):
    if models.Servicio.objects.count() == 0:
        return Response({'error':'No se encontraron servicios disponibles.'})
    servicios = models.Servicio.objects.all()
    # many = True es para cuando se pasa en forma de lista o queryset iterable
    serializer = serializers.ServicioSerializer(servicios, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_get_fechas_bloqueadas(request):
    if models.FechaBloqueada.objects.count() == 0:
        return Response({'error':'No se encontraron fechas para ese mes.'})
    fechas_bloqueadas = models.FechaBloqueada.objects.all()
    serializer = serializers.FechaBloqueadaSerializer(fechas_bloqueadas, many=True)
    return Response(serializer.data)

#==================================================================================

@api_view(['GET'])
def api_get_fechas_mes(request, mes):
    if models.FechaBloqueada.objects.count() == 0:
        return Response({'error':'No se encontraron fechas para ese mes.'}) 
    fechas_bloqueadas = models.FechaBloqueada.objects.filter(fecha__month=mes)
    serializer = serializers.FechaBloqueadaSerializer(fechas_bloqueadas, many=True)
    return Response(serializer.data)
# endregion
