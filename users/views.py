from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.timezone import now
from urllib.parse import urlencode
from core import models, forms, services
import os, datetime
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import timedelta

def calendario_admin(request : HttpRequest):
    return render(request, 'components/base.html')

def agenda(request : HttpRequest):
    return render(request, 'ver_agenda.html', context={'cita':models.Cita.objects.last()})

"""
POST PARA CAMBIAR EL ARCHIVO DE COMPROBANTE
"""
def actualizar_comprobante(request:HttpRequest):
    if request.method == 'POST':
        form = forms.ComprobanteForm(request.POST, request.FILES)
        if form.is_valid():
            eliminar_archivo = form.cleaned_data['eliminar_archivo']
            cita = models.Cita.objects.get(
                id=form.cleaned_data['id_cita']
            )
            if cita is not None:
                if cita.comprobante:
                    cita.comprobante.delete(save=False)
                    cita.comprobante = None
                if not eliminar_archivo:
                    archivo = form.cleaned_data['comprobante']
                    cita.comprobante = archivo
                cita.save()
                return redirect('ver_mis_citas')
        else:
            form.show_errors(request)
    return redirect('ver_mis_citas')



"""
CREAR CITA
"""
@login_required
def agendar_cita(request : HttpRequest):
    cliente = request.user
    if request.method == 'POST':
        form = forms.CitasForm(cliente, request.POST)
        if form.is_valid():
            cita = form.to_cita()
            if cita:
                messages.success(
                    request=request, 
                    message=f"Se agendó una cita para el {cita.fecha_cita.strftime('%d/%m/%Y con horario de %I:%M %p.')}"
                )
                notificacion = services.Notificacion(cliente)
                if notificacion.enviar_confirmacion(cita):
                    messages.success(
                        request=request, 
                        message=f'Se envió un correo de confirmación a {cliente.email}'
                    )
                else:
                    print(f'No se pudo enviar un email de confirmación a {cliente.email}.')
                return redirect('agendar_cita')
        else:
            form.show_errors(request)
    elif request.method == 'GET':
        form : forms.CitasForm = forms.CitasForm(cliente=cliente)
    fechas_bloqueadas = None
    return render(request, 'cita.html', { 
        'form':form,
        'fechas_bloqueadas':fechas_bloqueadas,
    })

"""
CREAR CITA COMO SUPERUSUARIO
"""

def agendar_super(request: HttpRequest):
    if request.method == 'POST':
        form_cita = forms.CitasAdminForm(request.POST)
        if form_cita.is_valid():
            cliente = form_cita.cleaned_data['cliente']
            form_cita.cliente = cliente
            cita = form_cita.to_cita()
            if cita:
                messages.success(
                    request=request, 
                    message=f"Se agendó una cita para el {cita.fecha_cita.strftime('%d/%m/%Y con horario de %I:%M %p.')}"
                )
                notificacion = services.Notificacion(cliente)
                if notificacion.enviar_confirmacion(cita):
                    messages.success(
                        request=request, 
                        message=f'Se envió un correo de confirmación a {cliente.email}'
                    )
                else:
                    print(f'No se pudo enviar un email de confirmación a {cliente.email}.')
                return redirect('agendar_super')
        else:
            form_cita.show_errors(request)
    elif request.method == 'GET':
        form_cita = forms.CitasAdminForm()
    fechas_bloqueadas = None
    return render(request, 'agendar_super.html', {
        'form_cita': form_cita,
        'fechas_bloqueadas':fechas_bloqueadas,
    })

"""
REGISTRAR CUENTA Y CITA A LA MISMA VEZ (SUPER USUARIO)
"""

def registro_y_cita(request: HttpRequest):
    if request.method == 'POST':
        form_registro = forms.RegistroForm(request.POST)
        form_cita = forms.CitasForm(None, request.POST)
        if form_registro.is_valid() and form_cita.is_valid():
            nuevo_cliente = models.Usuario(
                username=form_registro.cleaned_data['usuario'],
                email=form_registro.cleaned_data['email'],
                telefono=form_registro.cleaned_data['telefono'],
                nombre=form_registro.cleaned_data['nombre'],
                apellidos=form_registro.cleaned_data['apellidos']
            )
            nuevo_cliente.set_password(form_registro.cleaned_data['password'])
            nuevo_cliente.save()
            form_cita.cliente = nuevo_cliente
            cita = form_cita.to_cita()
            if cita:
                messages.success(
                    request=request,
                    message=f'Se registró a {nuevo_cliente.nombre} y se agendó su cita para el {cita.fecha_cita.strftime("%Y/%m/%d")} con horario de {cita.fecha_cita.strftime("%I:%M %p")}.'
                )
                notificacion = services.Notificacion(nuevo_cliente)
                if notificacion.enviar_confirmacion(cita):
                    messages.success(request, f'Se envió confirmación a {nuevo_cliente.email}')
                else:
                    print(f'No se pudo enviar un email a {nuevo_cliente.email}')

                return redirect('registro_y_cita')
            else:
                form_cita.add_error(None, "No se pudo agendar la cita. Revisa los datos.")
        else:
            form_registro.show_errors(request)
            form_cita.show_errors(request)
    elif request.method == 'GET':
        form_registro = forms.RegistroForm()
        form_cita = forms.CitasForm(None)
    fechas_bloqueadas = None
    return render(request, 'registro_y_cita.html', {
        'form_registro': form_registro,
        'form_cita': form_cita,
        'fechas_bloqueadas': fechas_bloqueadas,
    })

"""
EDITAR CITA PARA USUARIOS
Esta parece que ya no se usará
"""
@login_required
def editar_cita(request:HttpRequest):
    citas = models.Cita.objects.filter(cliente = request.user)
    if citas is not None:
        servicio : models.Servicio = citas[0].servicios.first()
        if servicio:
            print(servicio.get_categoria())
        for cita in citas:
            setattr(cita, 'categoria', cita.servicios.first().categoria)
            lista_servicios = []
            for s in cita.servicios.all():
                lista_servicios.append(s.id)
                setattr(cita, 'json_servicios', json.dumps(lista_servicios, cls=DjangoJSONEncoder))
    form_editar = forms.CitasForm(request.user)
    return render(request, 'editar_cita.html', {
        'citas':citas,
        'form':form_editar,
    })

"""
ELIMINAR CITA
"""
@login_required
def eliminar_cita(request : HttpRequest):
    cita_id = request.POST.get('cita_id', None)
    cita = models.Cita.objects.filter(id=cita_id).first()
    if cita is not None:
        mensaje_log = f'Se eliminó la cita de: {cita.cliente.get_full_name()}'\
                    f" para el {cita.fecha_cita.strftime('día %Y/%m/%d, hora %I:%M %p')}"
        messages.error(request, mensaje_log)
        print(mensaje_log)
        cita.delete()
    # redirigir a la URL anterior
    return redirect(request.META.get('HTTP_REFERER', '/')) 


"""
AÑADIR COMPROBANTE A CITA
aquí deberían verse las citas que ha hecho un usuario y poder eliminarlas 
o actualizar su estado añadiendo el comprobante.
"""
@login_required
def ver_citas_usuarios(request:HttpRequest):
    citas = models.Cita.objects.filter(cliente = request.user).order_by('fecha_cita')
    hoy = now()
    citas_pasadas = citas.filter(fecha_cita__lt=hoy)
    citas_futuras = citas.filter(fecha_cita__gte=hoy)
    print(citas_pasadas)
    print(citas_futuras)

    form_editar = forms.ComprobanteForm()
    return render(request, 'comprobar_citas.html', {
        'citas':citas_futuras,
        'citas_pasadas':citas_pasadas,
        'form':form_editar,
    })

@login_required
def ver_agenda_inicio(request:HttpRequest):
    if not request.user.is_superuser:
        return redirect('index')
    
    if request.method == 'POST':
        mes : str = request.POST.get('mes', 'NA')
        año : str = request.POST.get('año', 'NA')
        if mes.isdigit() and año.isdigit():
            return redirect('ver_agenda_redirect', mes=mes, año=año)
    
    fecha_actual = datetime.datetime.now().date()
    return redirect('ver_agenda_redirect', mes=fecha_actual.month, año=fecha_actual.year)

def ver_agenda(request : HttpRequest, mes, año):

    for mierda in models.Cita.objects.all():
        print(mierda)

    citas = models.Cita.objects.filter(
        fecha_cita__year = año,
        fecha_cita__month = mes,
    )\
    .order_by('fecha_cita')

    print(citas)

    form_comprobante = forms.ComprobanteForm()
    fecha_actual = datetime.datetime(year=año, month=mes, day=1)
    return render(request, 'ver_agenda.html', {
        'citas':citas,
        'form':form_comprobante,
        'fecha_actual': fecha_actual,
    })
    
"""
VISTA PARA CRUD DE FECHAS BLOQUEADAS
"""
@login_required
def bloquear_fecha(request: HttpRequest):
    if request.method == 'POST':
        return crear_editar_fecha(request)

    mes = request.GET.get('mes')
    año = request.GET.get('año')

    if (mes and mes.isdigit()) and (año and año.isdigit()):
        fechas_bloqueadas = models.FechaBloqueada.objects.filter(
            fecha__month=int(mes),
            fecha__year=int(año)
        ).order_by('fecha')
    else:
        fechas_bloqueadas = models.FechaBloqueada.objects.all().order_by('fecha')

    for fb in fechas_bloqueadas:
        lista_horas = [hb.hora for hb in fb.horas_bloqueadas.all()]
        setattr(fb, 'json', json.dumps(lista_horas, cls=DjangoJSONEncoder))

    form = forms.BloquearFechaForm()
    form_meses = forms.BloquearRangoForm()
    return render(request, 'bloquear-fechas.html', context={
        'fechas_bloqueadas': fechas_bloqueadas,
        'form': form,
        'form_meses': form_meses,
        'meses_disponibles': [
            ('enero', 1), ('febrero', 2), ('marzo', 3), ('abril', 4),
            ('mayo', 5), ('junio', 6), ('julio', 7), ('agosto', 8),
            ('septiembre', 9), ('octubre', 10), ('noviembre', 11), ('diciembre', 12)
        ],
        'años_disponibles': [2024, 2025],
        'hoy': datetime.date.today(),
    })

"""
Este es el POST del anterior método
"""
@login_required
def crear_editar_fecha(request: HttpRequest):
    kind = request.POST.get('form_kind', '').strip().lower()

    if kind == 'rango':
        form_meses = forms.BloquearRangoForm(request.POST)
        if form_meses.is_valid():
            fecha_inicio = form_meses.cleaned_data['fecha_inferior']
            fecha_fin    = form_meses.cleaned_data['fecha_superior']
            motivo       = form_meses.cleaned_data['motivo']

            cant_dias = (fecha_fin - fecha_inicio).days + 1
            for i in range(cant_dias):
                fecha = fecha_inicio + timedelta(days=i)
                fb, is_new = models.FechaBloqueada.objects.get_or_create(fecha=fecha)
                if not is_new:
                    fb.horas_bloqueadas.all().delete()
                fb.motivo = motivo
                fb.save()
                for hora in models.HorarioDisponible.objects.filter(activa=True).values_list('hora', flat=True):
                    models.HoraBloqueada.objects.create(fecha_bloqueada=fb, hora=hora)

        else:
            form_meses.show_errors(request)

        return redirigir_bloquear_fechas(request)

    if kind == 'dia':
        form = forms.BloquearFechaForm(request.POST)
        if form.is_valid():
            fb, is_new = models.FechaBloqueada.objects.get_or_create(fecha=form.cleaned_data['fecha'])
            if not is_new:
                fb.horas_bloqueadas.all().delete()
            fb.motivo = form.cleaned_data['motivo']
            fb.save()

            for horario in getattr(form, 'lista_horarios', []):
                models.HoraBloqueada.objects.create(fecha_bloqueada=fb, hora=horario)
        else:
            form.show_errors(request)

        return redirigir_bloquear_fechas(request)

    return redirigir_bloquear_fechas(request)



"""
ELIMINAR FECHAS BLOQUEADAS
"""
@login_required
def eliminar_fecha_bloqueada(request: HttpRequest):
    if request.method == 'POST':
        form = forms.BloquearFechaForm(request.POST)
        if form.is_valid():
            fecha_bloqueada = models.FechaBloqueada.objects.get(
                fecha = form.cleaned_data['fecha']
            )
            print(f'Eliminando {fecha_bloqueada}')
            fecha_bloqueada.delete()
        else:
            form.show_errors(request)
    return redirigir_bloquear_fechas(request)


def redirigir_bloquear_fechas(request: HttpRequest):
    params = {}
    mes = request.GET.get('mes')
    año = request.GET.get('año')
    if mes:
        params['mes'] = mes
    if año:
        params['año'] = año

    base_url = reverse('bloquear_fechas_get')
    url = f"{base_url}?{urlencode(params)}" if params else base_url
    return redirect(url)