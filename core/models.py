from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import datetime, time
import time as time_module

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

    def get_categoria(self):
        if self.categoria in self.Categorias.values:
            index = self.Categorias.values.index(self.categoria)
            return self.Categorias.choices[index][1]
        return self.Categorias.choices[0][1]


    def __str__(self):
        return (f"Servicio(id={self.id}, "\
                f"nombre='{self.nombre}', "\
                f"precio='{self.precio}, "\
                f"categoria={self.get_categoria_display()}')")


class Horario:
    MAÑANA = time(9, 0), '9:00 AM'
    MEDIODIA = time(12, 0), '12:00 PM'
    TARDE = time(16, 0), '4:00 PM'
    NOCHE = time(19, 0), '7:00 PM'
    
    choices = [MAÑANA, MEDIODIA, TARDE, NOCHE]
    values = [val[0] for val in choices]

class Cita(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    fecha_cita = models.DateTimeField(null=False, unique=True)
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=False)
    comprobante = models.FileField(null=True, upload_to='citas/comprobantes/')
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
        return int(time_module.mktime(self.fecha_cita.date().timetuple())) * 1000
#endregion

    def fecha_vencida(self):
        return timezone.now() > self.fecha_cita

    def tiempo_restante_legible(self):
        diferencia = self.fecha_cita - timezone.now()
        if diferencia.total_seconds() < 0:
            return "Ya pasó"

        dias = diferencia.days
        horas, resto = divmod(diferencia.seconds, 3600)
        minutos, _ = divmod(resto, 60)

        partes = []
        if dias: partes.append(f"{dias} días")
        if horas: partes.append(f"{horas} horas")
        if minutos: partes.append(f"{minutos} minutos")

        return ", ".join(partes)

    def validar_horario(self):
        data = Cita.horarios_disponibles(self.fecha_cita.date())
        horarios = [d[0] for d in data]
        print(f'{self.hora}  {horarios}')
        if self.hora in horarios:
            print('El horario esta disponible XD')


    @staticmethod
    def horarios_disponibles(dia:datetime.date):
        citas = Cita.objects.filter(
            fecha_cita__date = dia # filtra por la fecha dd/mm/yyyy
        ).values_list(          # obtiene una lista de las horas ocupadas
            'fecha_cita__time', # selecciona solo la hora (datetime.time)
            flat=True
        )
        horarios = []
        for  hora, string in Cita.Horario.values:
            if hora not in citas: # si la hora no está en las citas ocupadas
                horarios.append((hora, string))
        return horarios

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
    motivo = models.CharField(max_length=100, default='N/A')
    fecha_creacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fechas_bloqueadas'

    @property
    def UNIX_timestamp(self):
        """ DATO ÚTIL PARA CASTEAR A FECHAS DE JAVASCRIPT """
        return int(time.mktime(self.fecha.timetuple())) * 1000
    
    @property
    def dia_entero_bloqueado(self) -> bool:
        if not hasattr(self, 'horas_bloqueadas'):
            return False
        horarios = self.horas_bloqueadas.all()
        todos_los_horarios = True
        for horario in horarios:
            if horario.hora not in Horario.values:
                todos_los_horarios = False
                break
        return todos_los_horarios

    def __str__(self) -> str:
        return f'[{self.id}] Fecha bloqueada: {self.fecha.isoformat()}, motivo: {self.motivo}'


class HoraBloqueada(models.Model):
    fecha_bloqueada = models.ForeignKey(FechaBloqueada, on_delete=models.CASCADE, related_name='horas_bloqueadas')
    hora = models.TimeField(choices=Horario.choices)

    class Meta:
        db_table = 'horas_bloqueadas'
        
    def __str__(self) -> str:
        return f'[{self.id}] Hora bloqueada: {self.hora} para [{self.fecha_bloqueada.id}]'
    
