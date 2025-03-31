from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import time

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
                f"telefono='{self.telefono}',\n\tnombre='{self.get_full_name()}',\n\t"
                f"fecha_creacion='{self.fecha_creacion}'\n)")


class Servicio(models.Model):
    class Categorias(models.TextChoices):
        NA = '?', 'Sin asignar' # por si acaso
        MANOS = 'M', 'Manos'
        FRAN_BABY_BOOMER = 'F', 'Full Set Francesas/Baby Boomer'
        PIES = 'P', 'Pies'
        RETIRO = 'R', 'Retiro'

    id = models.AutoField(primary_key=True, blank=True)
    nombre = models.CharField(max_length=64, null=False)
    precio = models.DecimalField(null=True, decimal_places=2, max_digits=6)
    categoria = models.CharField(null=True, max_length=2, choices=Categorias.choices, default=Categorias.MANOS)

    class Meta:
        """Clase especial que usa Django para asociar a la BD"""
        db_table = 'servicios'

    def __str__(self):
        return (f"Servicio(id={self.id}, "\
                f"nombre='{self.nombre}', "\
                f"precio='{self.precio}, "\
                f"categoria={self.get_categoria_display()}')")

class Cita(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    fecha_cita = models.DateTimeField(null=False, unique=True)
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=False)
    servicios = models.ManyToManyField(Servicio, related_name='citas')
    fecha_creacion = models.DateTimeField(auto_now=True)

    class Meta:
        """Clase especial que usa Django para asociar a la BD"""
        db_table = 'citas'

#region propiedades
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
#endregion
    
    def get_precio(self) -> float:
        if self.servicios:
            precio = 0
            for serv in self.servicios.all():
                precio += serv.precio
        return precio
        
    def __str__(self) -> str:
        try:
            str_s = ''
            for serv in self.servicios.all():
                str_s += f' {serv.nombre},'
            return f'Cita para {self.cliente.get_full_name()} el {self.fecha_cita} por{str_s} por ${self.get_precio()}'
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

