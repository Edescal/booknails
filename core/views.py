from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.http.request import HttpRequest
from . import models, forms, services, utils
from .forms import CategoriaForm, ServicioForm
from api import serializers
from .models import Servicio, Categoria
from decimal import Decimal, InvalidOperation
import re
import datetime as dt

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
                return redirect('home')
        else:
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
            form.save()
            nueva_contraseña = form.cleaned_data['password']
            if nueva_contraseña:
                if nueva_contraseña == form.cleaned_data['confirmar_password']:
                    usuario.set_password(nueva_contraseña) 
                    usuario.save() 
                else:
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return redirect('editar_usuario')
            usuario.save()
            messages.success(request, 'Tus datos han sido actualizados correctamente.')
            return redirect('home')
    else:
        form = forms.EditarUsuarioForm(instance=usuario)

    return render(request, 'editar_usuario.html', {'form': form})

@login_required
def ver_perfil(request : HttpRequest):
    categorias = Categoria.objects.filter(activa=True).order_by('nombre')
    return render(request, 'ver_perfil.html', {"categorias": categorias})

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

'''
XD
'''
@login_required
def quick_add_categoria(request):
    form = CategoriaForm(request.POST)
    if form.is_valid():
        cat = form.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'id': cat.id, 'label': cat.nombre})
        messages.success(request, 'Categoría creada.')
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
        messages.error(request, 'Revisa los datos de la categoría.')
    return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER', '/'))

@login_required
def quick_add_servicio(request):
    nombre = (request.POST.get('nombre') or '').strip()
    precio_raw = (request.POST.get('precio') or '').strip()
    categoria_id = request.POST.get('categoria')

    errors = {}

    if not nombre:
        errors['nombre'] = ['Requerido']

    try:
        precio = parse_decimal_humano(precio_raw)
    except InvalidOperation:
        errors['precio'] = ['Formato inválido. Ej: 280.50 o 280,50']
    else:
        if precio < 0:
            errors['precio'] = ['Debe ser positivo']
        else:
            precio = precio.quantize(Decimal('0.01'))

    try:
        cat = Categoria.objects.get(pk=categoria_id, activa=True)
    except Categoria.DoesNotExist:
        errors['categoria'] = ['Categoría inválida o inactiva']

    if errors:
        return JsonResponse({'ok': False, 'errors': errors}, status=400)

    serv = Servicio.objects.create(nombre=nombre, precio=precio, categoria=cat)

    return JsonResponse({
        'ok': True,
        'id': serv.id,
        'label': serv.nombre,
        'categoria': serv.categoria.nombre if serv.categoria_id else None,
        'precio': str(serv.precio),
    })

def _parse_hora_flexible(raw: str) -> dt.time:
    """Acepta 'HH:MM', 'HH:MM:SS' (24h) y 'H:MM AM/PM', 'H AM/PM' (12h)."""
    s = (raw or "").strip().upper()
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I %p", "%I:%M%p", "%I%p"):
        try:
            return dt.datetime.strptime(s, fmt).time()
        except ValueError:
            pass
    if s.endswith(("AM", "PM")) and ":" in s:
        try:
            hhmm, ampm = s[:-2].strip(), s[-2:]
            h, m = [int(x) for x in hhmm.split(":")]
            if ampm == "PM" and h != 12:
                h += 12
            if ampm == "AM" and h == 12:
                h = 0
            return dt.time(h, m, 0)
        except Exception:
            pass
    raise ValueError("Formato hora inválido")

@login_required
def quick_add_horario(request):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'ok': False, 'errors': {'__all__': ['Solicitud inválida']}}, status=400)

    raw_hora = (request.POST.get('hora') or '').strip()
    raw_dia  = (request.POST.get('dia') or '').strip()

    try:
        dia = int(raw_dia)
        if not 1 <= dia <= 7:
            raise ValueError
    except ValueError:
        return JsonResponse({'ok': False, 'errors': {'dia': ['Día inválido']}}, status=400)

    try:
        t = _parse_hora_flexible(raw_hora)
    except ValueError:
        return JsonResponse({'ok': False, 'errors': {'hora': ['Hora inválida. Usa 03:30 o 3:30 AM/PM']}}, status=400)

    obj, created = models.HorarioDisponible.objects.get_or_create(
        dia_semana=dia, hora=t, defaults={'activa': True}
    )

    label = f"{obj.get_dia_semana_display()} {t.strftime('%I:%M %p').lstrip('0')}"
    return JsonResponse({
        'ok': True,
        'id': obj.id,
        'value': t.strftime("%H:%M:%S"),
        'label': label,
        'dia': dia
    })

def parse_decimal_humano(raw: str) -> Decimal:
    s = (raw or '').strip()
    if not s:
        raise InvalidOperation("empty")

    s = re.sub(r'[^\d,.-]', '', s)

    if s.count(',') and not s.count('.'):
        s = s.replace(',', '.')
    elif s.count(',') and s.count('.'):
        last_comma = s.rfind(',')
        last_dot = s.rfind('.')
        if last_comma > last_dot:
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    s = s.replace('-.', '-0.') if s.startswith('-.') else s
    if s.startswith('.'):
        s = '0' + s

    dec = Decimal(s) 
    return dec