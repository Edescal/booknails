from django.db import models
import time

# Create your models here.
class Usuario(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    username = models.CharField(max_length=32, unique=True, null=False)
    password = models.CharField(max_length=255, null= False, default='password')
    email = models.EmailField(unique=True, null=False)
    telefono = models.CharField(max_length=10, unique=False, null=False)
    nombre = models.CharField(max_length=64)
    apellidos = models.CharField(max_length=64)
    fecha_creacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return (f"Usuario(id={self.id}, username='{self.username}', email='{self.email}', "
                f"telefono='{self.telefono}', nombre='{self.nombre}', apellidos='{self.apellidos}', "
                f"fecha_creacion='{self.fecha_creacion}')")


class Servicio(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    nombre = models.CharField(max_length=64, null=False, unique=True)
    precio = models.DecimalField(null=True, decimal_places=2, max_digits=2)

    class Meta:
        db_table = 'servicios'

    def __str__(self):
        return (f"Servicio(id={self.id}, nombre='{self.nombre}', precio='{self.precio}')")



class Cita(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    fecha_cita = models.DateTimeField(null=False, unique=True)
    id_cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=False)
    id_servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, null=False)

    class Meta:
        db_table = 'citas'

    @property
    def fecha(self):
        return self.fecha_cita.date()
    
    @property
    def hora(self):
        return self.fecha_cita.time()
    
    @property
    def UNIX_timestamp(self):
        return int(time.mktime(self.fecha.timetuple())) * 1000


class Notificacion:
    def __init__(self, email, telefono):
        self.email = email
        self.telefono = telefono

    def enviar_confirmacion(self):
        pass

    def enviar_recordatorio(self):
        pass

