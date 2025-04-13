from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from core import models, utils
from . import serializers
from datetime import datetime, date, time
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
        for  hora, string in models.Cita.Horario.values:
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
@login_required
def api_get_fechas_bloqueadas(request):
    if models.FechaBloqueada.objects.count() == 0:
        return Response({'error':'No se encontraron fechas para ese mes.'})
    fechas_bloqueadas = models.FechaBloqueada.objects.all()
    serializer = serializers.FechaBloqueadaSerializer(fechas_bloqueadas, many=True)
    return Response(serializer.data)


"""
====================================
MÉTODOS PARA INFORMACIÓN ESPECÍFICA
====================================
"""
@api_view(['GET'])
def api_get_horarios(request, year, mes, dia):
    selected_citas = horarios_disponibles(date(year, mes, dia))
    return Response(selected_citas)


def horarios_disponibles(dia:datetime.date):
    citas = models.Cita.objects.filter(
        fecha_cita__date = dia # filtra por la fecha dd/mm/yyyy
    ).values_list(          # obtiene una lista de las horas ocupadas
        'fecha_cita__time', # selecciona solo la hora (datetime.time)
        flat=True
    )
    horarios = []
    for  hora, string in models.Cita.Horario.values:
        if hora not in citas: # si la hora no está en las citas ocupadas
            horarios.append((hora, string))
    return horarios


