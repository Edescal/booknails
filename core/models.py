from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import time

class UsuarioManager(BaseUserManager):
    pass

# Create your models here.
class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True, blank=True)
    username = models.CharField(max_length=32, unique=True, null=False, blank=False)
    password = models.CharField(max_length=255, null= False, default='password', blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    telefono = models.CharField(max_length=10, unique=False, null=False)
    nombre = models.CharField(max_length=64)
    apellidos = models.CharField(max_length=64)
    fecha_creacion = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'  # Campo utilizado para el login
    REQUIRED_FIELDS = ['email', 'password']  # Campos requeridos al crear un usuario

    class Meta:
        db_table = 'usuarios'

    @staticmethod
    def build(**kwargs) -> 'Usuario':
        user = Usuario()
        if kwargs.get('username'):
            user.username = kwargs.get('username')
        elif kwargs.get('password'):
            user.set_password(kwargs.get('password'))
        elif kwargs.get('email'):
            user.username = kwargs.get('email')
        elif kwargs.get('telefono'):
            user.username = kwargs.get('telefono')
        elif kwargs.get('nombre'):
            user.username = kwargs.get('nombre')
        elif kwargs.get('apellidos'):
            user.username = kwargs.get('apellidos')
        return user

    def get_full_name(self) -> str:
        return f'{self.nombre} {self.apellidos}'

    def __str__(self) -> str:
        return (f"Usuario(\n\tid={self.id},\n\tusername='{self.username}',\n\temail='{self.email}',\n\t"
                f"telefono='{self.telefono}',\n\tnombre='{self.nombre}',\n\tapellidos='{self.apellidos}',\n\t"
                f"password='{self.password}',\n\tfecha_creacion='{self.fecha_creacion}'\n)")


class Servicio(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    nombre = models.CharField(max_length=64, null=False, unique=True)
    precio = models.DecimalField(null=True, decimal_places=2, max_digits=6)

    class Meta:
        db_table = 'servicios'

    def __str__(self):
        return (f"Servicio(id={self.id}, nombre='{self.nombre}', precio='{self.precio}')")


class Cita(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    fecha_cita = models.DateTimeField(null=False, unique=True)
    id_cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=False)
    id_servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, null=False)
    fecha_creacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'citas'

    @property
    def fecha(self):
        return self.fecha_cita.date().isoformat()
    
    @property
    def hora(self):
        return self.fecha_cita.time()
    
    @property
    def UNIX_timestamp(self):
        """ DATO ÚTIL PARA CASTEAR A FECHAS DE JAVASCRIPT """
        return int(time.mktime(self.fecha_cita.date().timetuple())) * 1000
    
    def __str__(self) -> str:
        try:
            return f'Cita para {self.id_cliente.get_full_name()} el {self.fecha_cita} para {self.id_servicio}'
        except Exception as e:
            return 'Cita incompleta'


class FechaBloqueada(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    fecha = models.DateField(null=False, unique=True)
    fecha_creacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fechas_bloqueadas'

    @property
    def UNIX_timestamp(self):
        """ DATO ÚTIL PARA CASTEAR A FECHAS DE JAVASCRIPT """
        return int(time.mktime(self.fecha.timetuple())) * 1000

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
