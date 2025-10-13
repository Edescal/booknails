from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from core import models, utils
from . import serializers
from datetime import datetime, date, time
from django.shortcuts import get_object_or_404
import calendar
from core.models import Cita
from decimal import Decimal
"""
====================================
MÉTODOS PARA LAS APIS DE LOS MODELOS
====================================
"""
@api_view(['GET'])
@login_required
def api_get_citas(request, año, mes, dia):
    citas = models.Cita.objects.filter(fecha_cita__year=año, fecha_cita__month=mes, fecha_cita__day=dia)
    if citas.count() == 0:
        return Response({'error':'No se encontraron citas para la fecha solicitada.'})
    
    citas_validas = []
    for cita in citas:
        for  hora in models.Horario.values:
            if cita.hora == hora:
                citas_validas.append(cita)
    serializer = serializers.CitaSerializer(citas_validas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@login_required
def api_get_usuarios(request):
    usuarios = models.Usuario.objects.all()
    serializer = serializers.UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@login_required
def api_get_servicios(request):
    qs = models.Servicio.objects.select_related('categoria').order_by('nombre')
    if not qs.exists():
        return Response({'error': 'No se encontraron servicios disponibles.'}, status=404)
    ser = serializers.ServicioSerializer(qs, many=True)
    return Response(ser.data)


@api_view(['GET'])
@login_required
def api_get_servicios_cat(request, categoria: str):
    cat_obj = None
    try:
        cat_id = int(categoria)
        cat_obj = models.Categoria.objects.filter(id=cat_id).first()
    except (TypeError, ValueError):
        pass
    if cat_obj is None:
        cat_obj = models.Categoria.objects.filter(nombre__iexact=str(categoria)).first()

    if not cat_obj:
        return Response({'error': 'Categoría no encontrada.'}, status=404)

    qs = models.Servicio.objects.filter(categoria=cat_obj).order_by('nombre')
    ser = serializers.ServicioSerializer(qs, many=True)
    return Response(ser.data)

@api_view(['GET'])
def api_is_fecha_bloqueada(request, año, mes, dia):    
    fecha_bloqueada = models.FechaBloqueada.objects.filter(fecha__year=año, fecha__month=mes, fecha__day=dia)
    if len(fecha_bloqueada) > 0:
        return Response({'resultado':'ok'})
    else: return Response({})

@api_view(['GET'])
def api_fechas_bloqueadas_mes(request, año, mes):
    qs = models.FechaBloqueada.objects.filter(
        fecha__year=año, fecha__month=mes
    ).prefetch_related('horas_bloqueadas')

    # Solo días bloqueados COMPLETOS
    solo_dias_enteros = [f for f in qs if f.dia_entero_bloqueado]

    # Entregar exactamente lo que el front espera: unix_timestamp (ms)
    payload = [
        {'unix_timestamp': int(datetime.combine(f.fecha, time.min).timestamp() * 1000)}
        for f in solo_dias_enteros
    ]
    return Response(payload)

@api_view(['GET'])
def api_mes_completamente_bloqueado(request, año, mes):
    _, total_dias = calendar.monthrange(año, mes)
    fechas_mes = [date(año, mes, dia) for dia in range(1, total_dias + 1)]
    horarios_posibles = models.Horario.values
    fechas_bloqueadas = models.FechaBloqueada.objects.filter(fecha__year=año, fecha__month=mes)

    conjunto = set()
    for fecha in fechas_bloqueadas:
        horarios = fecha.horas_bloqueadas.all()
        todos_los_horarios = True
        for horario in horarios:
            if horario.hora not in horarios_posibles:
                todos_los_horarios = False
                break

            if todos_los_horarios:
                conjunto.add(fecha.fecha)

    print(conjunto.__len__())
    bloqueado_completo = all(d in fechas_bloqueadas for d in fechas_mes)
    print(bloqueado_completo)

    return Response({'puta':'ok'})

"""
====================================
MÉTODOS PARA INFORMACIÓN ESPECÍFICA
====================================
"""
@api_view(["GET"])
def api_get_horarios(request, year, mes, dia):
    try:
        f = date(int(year), int(mes), int(dia))
    except ValueError:
        return Response([], status=400)

    choices = models.Cita.horarios_disponibles(f)  # [(value,label),...]
    return Response([{"value": v, "label": t} for (v, t) in choices])


def horarios_disponibles(d: date):
    dow = d.isoweekday()

    base = list(
        models.HorarioDisponible.objects
        .filter(activa=True, dia_semana=dow)
        .order_by('hora')
        .values_list('hora', flat=True)
    )

    fb = models.FechaBloqueada.objects.filter(fecha=d).first()
    if fb and fb.dia_entero_bloqueado:
        return []

    bloqueadas = set(fb.horas_bloqueadas.values_list('hora', flat=True)) if fb else set()

    ocupadas = set(
        models.Cita.objects
        .filter(fecha_cita__date=d)
        .values_list('fecha_cita__time', flat=True)
    )

    libres = [h for h in base if h not in bloqueadas and h not in ocupadas]
    return [(h.strftime('%H:%M:%S'), h.strftime('%I:%M %p').lstrip('0')) for h in libres]

@api_view(['GET'])
@login_required
def api_horarios_por_dia(request, yyyy, mm, dd):
    d = date(int(yyyy), int(mm), int(dd))
    pares = Cita.horarios_disponibles(d)
    data = [{'value': t.strftime("%H:%M:%S"), 'label': lbl} for (t, lbl) in pares]
    return Response(data)

"""
MIERDA
"""


@api_view(['GET'])
@login_required
def admin_list(request, kind):
    if kind == 'categorias':
        qs = models.Categoria.objects.all().order_by('nombre')
        data = [{'id':c.id,'nombre':c.nombre,'activa':c.activa} for c in qs]
        return Response(data)

    if kind == 'servicios':
        qs = models.Servicio.objects.select_related('categoria').order_by('nombre')
        data = [{'id':s.id,'nombre':s.nombre,'precio':str(s.precio or ''),'categoria_id':s.categoria_id,
                 'categoria': s.categoria.nombre if s.categoria_id else None} for s in qs]
        return Response(data)

    if kind == 'horarios':
        qs = models.HorarioDisponible.objects.order_by('dia_semana','hora')
        data = [{'id':h.id,'dia_semana':h.dia_semana,'dia_label':h.get_dia_semana_display(),
                 'hora':h.hora.strftime('%H:%M:%S'),'activa':h.activa} for h in qs]
        return Response(data)

    return Response({'error':'kind inválido'}, status=400)

@api_view(['PATCH','POST'])
@login_required
def admin_update(request, kind, pk):
    if kind == 'categorias':
        obj = get_object_or_404(models.Categoria, pk=pk)
        nombre = request.data.get('nombre')
        activa = request.data.get('activa')
        if nombre is not None: obj.nombre = nombre.strip()
        if activa is not None: obj.activa = bool(str(activa).lower() in ('1','true','on','yes'))
        obj.save()
        return Response({'ok':True})

    if kind == 'servicios':
        obj = get_object_or_404(models.Servicio, pk=pk)
        nombre = request.data.get('nombre')
        precio = request.data.get('precio')
        categoria = request.data.get('categoria')

        if nombre is not None: obj.nombre = nombre.strip()
        if precio is not None:
            obj.precio = Decimal(str(precio).replace(',', '.')) if str(precio).strip() else None
        if categoria is not None:
            obj.categoria = models.Categoria.objects.get(pk=int(categoria))
        obj.save()
        return Response({'ok':True})

    if kind == 'horarios':
        obj = get_object_or_404(models.HorarioDisponible, pk=pk)
        dia_semana = request.data.get('dia_semana')
        hora = request.data.get('hora')
        activa = request.data.get('activa')

        if dia_semana is not None: obj.dia_semana = int(dia_semana)
        if hora is not None:
            s = str(hora).strip()
            obj.hora = datetime.strptime(s, '%H:%M:%S').time() if len(s)==8 else datetime.strptime(s, '%H:%M').time()
        if activa is not None: obj.activa = bool(str(activa).lower() in ('1','true','on','yes'))
        obj.save()
        return Response({'ok':True})

    return Response({'error':'kind inválido'}, status=400)

@api_view(['POST','DELETE'])
@login_required
def admin_delete(request, kind, pk):
    if kind == 'categorias':
        obj = get_object_or_404(models.Categoria, pk=pk)
        obj.activa = False
        obj.save()
        return Response({'ok':True, 'activa':False})

    if kind == 'horarios':
        obj = get_object_or_404(models.HorarioDisponible, pk=pk)
        obj.activa = False
        obj.save()
        return Response({'ok':True, 'activa':False})

    if kind == 'servicios':
        obj = get_object_or_404(models.Servicio, pk=pk)
        obj.delete()
        return Response({'ok':True, 'deleted':True})

    return Response({'error':'kind inválido'}, status=400)