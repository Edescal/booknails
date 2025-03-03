from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import time

class UsuarioManager(BaseUserManager):
    pass

# Create your models here.
class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.IntegerField(primary_key=True, auto_created=True)
    username = models.CharField(max_length=32, unique=True, null=False)
    password = models.CharField(max_length=255, null= False, default='password')
    email = models.EmailField(unique=True, null=False)
    telefono = models.CharField(max_length=10, unique=False, null=False)
    nombre = models.CharField(max_length=64)
    apellidos = models.CharField(max_length=64)
    fecha_creacion = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'  # Campo utilizado para el login
    REQUIRED_FIELDS = ['email', 'password']  # Campos requeridos al crear un usuario

    class Meta:
        db_table = 'usuarios'

    def get_full_name(self) -> str:
        return f'{self.nombre} {self.apellidos}'

    def __str__(self) -> str:
        return (f"Usuario(\n\tid={self.id},\n\tusername='{self.username}',\n\temail='{self.email}',\n\t"
                f"telefono='{self.telefono}',\n\tnombre='{self.nombre}',\n\tapellidos='{self.apellidos}',\n\t"
                f"fecha_creacion='{self.fecha_creacion}'\n)")


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
    fecha_creacion = models.DateTimeField(auto_now=True)

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


class FechaBloqueada(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField(null=False, unique=True)
    fecha_creacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fechas_bloqueadas'

    def __str__(self) -> str:
        return f'Fecha bloqueada: {self.fecha.isoformat()}'


class Notificacion:
    def __init__(self, email, telefono):
        self.email = email
        self.telefono = telefono

    def enviar_confirmacion(self):
        pass

    def enviar_recordatorio(self):
        pass
