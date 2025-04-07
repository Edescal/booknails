"""
Aqui se ponen serializadores que crean 
en  automatico las vistas para las API 
al usar @api_view(['GET']) en views.py
"""
from rest_framework import serializers
from core import models

class CitaSerializer(serializers.ModelSerializer):
    # fecha en tiempo unix
    unix_timestamp = serializers.SerializerMethodField()
    # obtener el objeto del cliente
    cliente = serializers.SerializerMethodField()
    servicios = serializers.SerializerMethodField()
    precio = serializers.SerializerMethodField()

    class Meta:
        model = models.Cita
        fields = '__all__'

    def get_unix_timestamp(self, obj : models.Cita):
        return obj.UNIX_timestamp
    
    def get_cliente(self, obj : models.Cita):
        serializer = UsuarioSerializer(obj.cliente)
        return serializer.data
    
    def get_servicios(self, obj : models.Cita):
        serializer = ServicioSerializer(obj.servicios, many=True)
        return serializer.data
    
    def get_precio(self, obj : models.Cita):
        precio = obj.get_precio()
        return precio



class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Usuario
        fields = '__all__'
    
class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Servicio
        fields = '__all__'

class FechaBloqueadaSerializer(serializers.ModelSerializer):
    # fecha en tiempo unix
    unix_timestamp = serializers.SerializerMethodField()
    
    class Meta:
        model = models.FechaBloqueada
        fields = '__all__'

    def get_unix_timestamp(self, obj : models.FechaBloqueada):
        return obj.UNIX_timestamp
    


