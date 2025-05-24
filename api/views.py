from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from core import models, utils
from . import serializers
from datetime import datetime, date, time
import calendar
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
    if models.Servicio.objects.count() == 0:
        return Response({'error':'No se encontraron servicios disponibles.'})
    servicios = models.Servicio.objects.all()
    # many = True es para cuando se pasa en forma de lista o queryset iterable
    serializer = serializers.ServicioSerializer(servicios, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@login_required
def api_get_servicios_cat(request, categoria : str):
    if models.Servicio.objects.count() == 0:
        return Response({'error':'No se encontraron servicios disponibles.'})
    elif categoria.upper() in dict(models.Servicio.Categorias.choices):
        print(f'Sí se encuentra {categoria.upper()} en Categorias')
        servicios = models.Servicio.objects.filter(categoria=categoria.upper()).values()
        serializer = serializers.ServicioSerializer(servicios, many=True)
        return Response(serializer.data)
    return Response({'error':'No se encontraron servicios disponibles.'})

@api_view(['GET'])
def api_is_fecha_bloqueada(request, año, mes, dia):    
    fecha_bloqueada = models.FechaBloqueada.objects.filter(fecha__year=año, fecha__month=mes, fecha__day=dia)
    if len(fecha_bloqueada) > 0:
        return Response({'resultado':'ok'})
    else: return Response({})

@api_view(['GET'])
def api_fechas_bloqueadas_mes(request, año, mes):    
    fechas_bloqueadas = models.FechaBloqueada.objects.filter(fecha__year=año, fecha__month=mes)
    serializer = serializers.FechaBloqueadaSerializer(fechas_bloqueadas, many=True)
    return Response(serializer.data)  

@api_view(['GET'])
def api_mes_completamente_bloqueado(request, año, mes):
    _, total_dias = calendar.monthrange(año, mes)
    fechas_mes = [date(año, mes, dia) for dia in range(1, total_dias + 1)]
    # print(fechas_mes)

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

        # bloqueado_completo = all(d in fechas_con_bloqueo_total for d in fechas_mes)
    return Response({'puta':'ok'})

"""
====================================
MÉTODOS PARA INFORMACIÓN ESPECÍFICA
====================================
"""
@api_view(['GET'])
def api_get_horarios(request, year, mes, dia):
    selected_citas = horarios_disponibles(date(year, mes, dia))
    return Response(selected_citas)


def horarios_disponibles(fecha: datetime.date):
    # hay que ver si hay citas para esa fecha
    citas = models.Cita.objects.filter(
        fecha_cita__date = fecha # filtra por la fecha dd/mm/yyyy
    ).values_list(          # obtiene una lista de las horas ocupadas
        'fecha_cita__time', # selecciona solo la hora (datetime.time)
        flat=True
    )
    # hay que ver si una fecha bloqueada tiene ciertos horarios bloqueados
    fecha_bloqueada = models.FechaBloqueada.objects.filter(fecha__year=fecha.year, fecha__month=fecha.month, fecha__day=fecha.day).first()
    # hay que obtener las horas (datetime.time) en una lista para filtrar
    if fecha_bloqueada:
        horarios_bloqueados = [hora_bloqueada.hora for hora_bloqueada in fecha_bloqueada.horas_bloqueadas.all()]
    else:
        horarios_bloqueados = []
    # aquí se guardan los horarios que se devuelven (libres)
    horarios = []
    for hora, string in models.Horario.choices:
        print(f'hora: {type(hora)} {hora} string: {string}')
        if hora not in citas and hora not in horarios_bloqueados: # si la hora no está en las citas ocupadas
            print(f'\tdisponible')
            horarios.append((hora, string))
        else:
            print(f'\tocupado')
    return horarios


# Compara los horarios de un servicio con los horarios disponibles de un día
@api_view(['GET'])
def horario__disponible_servicio(request, id_servicio, año, mes, dia):
    # Se obtienen los horarios disponibles asociados al servicio
    servicio = models.Servicio.objects.filter(id=id_servicio).first()
    horarios_servicio = servicio.horario_disponible.all()

    # Se obtienen los horarios ocupados de una fecha
    horarios_citas = models.Cita.objects.filter(
        fecha_cita__date = date(año, mes, dia) # filtra por la fecha dd/mm/yyyy
    ).values_list(          # obtiene una lista de las horas ocupadas
        'fecha_cita__time', # selecciona solo la hora (datetime.time)
        flat=True,
    )

    # se devuelven los horarios de servicio que NO han sido ocupados por alguna cita
    horarios_libres = [horario for horario in horarios_servicio if horario.hora not in horarios_citas]
    
    # Se devuelve
    serializer = serializers.HoraServicioSerializer(horarios_libres, many=True)
    return Response(serializer.data)

