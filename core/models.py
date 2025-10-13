from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from datetime import datetime, time
from datetime import date as _date
import time as time_module

DIAS_SEMANA = [
    (0, "Lunes"), (1, "Martes"), (2, "Miércoles"),
    (3, "Jueves"), (4, "Viernes"), (5, "Sábado"), (6, "Domingo"),
]

class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True, blank=True)
    username = models.CharField(max_length=32, unique=True, null=False, blank=False)
    password = models.CharField(max_length=255, null= False, default='password', blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    telefono = models.CharField(max_length=10, unique=False, null=False)
    nombre = models.CharField(max_length=64)
    apellidos = models.CharField(max_length=64)
    fecha_creacion = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']

    class Meta:
        db_table = 'usuarios'

    def get_full_name(self) -> str:
        return f'{self.nombre} {self.apellidos}'

    def __str__(self) -> str:
        return (f"Usuario(\n\tid={self.id},\n\tusername='{self.username}',\n\temail='{self.email}',\n\t"
                f"telefono='{self.telefono}',\n\tnombre='{self.get_full_name()}',\n\t"
                f"fecha_creacion='{self.fecha_creacion}'\n)")

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=64, unique=True)
    activa = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.activa = True
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'categorias'

    def __str__(self):
        return self.nombre 

class Servicio(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=64)
    precio = models.DecimalField(null=True, decimal_places=2, max_digits=8)
    categoria = models.ForeignKey('Categoria', null=True, on_delete=models.SET_NULL,
                                  db_column='categoria_id')

    class Meta:
        db_table = 'servicios'

    def __str__(self):
        return self.nombre 

class HorarioDisponible(models.Model):
    class Dias(models.IntegerChoices):
        LUNES = 1, "Lunes"
        MARTES = 2, "Martes"
        MIERCOLES = 3, "Miércoles"
        JUEVES = 4, "Jueves"
        VIERNES = 5, "Viernes"
        SABADO = 6, "Sábado"
        DOMINGO = 7, "Domingo"

    id = models.AutoField(primary_key=True)
    dia_semana = models.PositiveSmallIntegerField(choices=Dias.choices, default=Dias.LUNES)
    hora = models.TimeField()
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'horarios_disponibles'
        ordering = ['dia_semana', 'hora']
        constraints = [
            models.UniqueConstraint(fields=['dia_semana', 'hora'], name='uniq_dia_hora')
        ]

    def __str__(self):
        return f"{self.get_dia_semana_display()} {self.hora.strftime('%I:%M %p').lstrip('0')}"

    @classmethod
    def as_choices(cls):
        times = sorted(set(cls.objects.filter(activa=True).values_list('hora', flat=True)))
        return [(t.strftime("%H:%M:%S"), t.strftime("%I:%M %p").lstrip("0")) for t in times]
    
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
    def horarios_disponibles(fecha: _date):
        """
        Devuelve lista de tuplas (value, label) -> ('HH:MM:SS', 'h:mm AM/PM')
        filtradas por día de semana, quitando horas ocupadas y bloqueadas.
        """
        from .models import HorarioDisponible, HoraBloqueada 

        dow = fecha.isoweekday()

        base = list(
            HorarioDisponible.objects
            .filter(dia_semana=dow, activa=True)
            .values_list('hora', flat=True)
        )

        ocupadas = set(
            Cita.objects
            .filter(fecha_cita__date=fecha)
            .values_list('fecha_cita__time', flat=True)
        )

        bloqueadas = set(
            HoraBloqueada.objects
            .filter(fecha_bloqueada__fecha=fecha)
            .values_list('hora', flat=True)
        )

        libres = []
        for h in base:
            if h in ocupadas or h in bloqueadas:
                continue
            value = h.strftime("%H:%M:%S")
            label = h.strftime("%I:%M %p").lstrip("0")
            libres.append((value, label))
        return libres
    
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
        horarios_bloq = self.horas_bloqueadas.all()

        from .models import HorarioDisponible
        dow = self.fecha.isoweekday()
        activos = set(
            HorarioDisponible.objects
            .filter(activa=True, dia_semana=dow)
            .values_list('hora', flat=True)
        )
        bloqueados = set(h.hora for h in horarios_bloq)
        return len(activos) > 0 and activos.issubset(bloqueados)

    def __str__(self) -> str:
        return f'[{self.id}] Fecha bloqueada: {self.fecha.isoformat()}, motivo: {self.motivo}'


class HoraBloqueada(models.Model):
    fecha_bloqueada = models.ForeignKey(FechaBloqueada, on_delete=models.CASCADE, related_name='horas_bloqueadas')
    hora = models.TimeField()

    class Meta:
        db_table = 'horas_bloqueadas'
        
    def __str__(self) -> str:
        return f'[{self.id}] Hora bloqueada: {self.hora} para [{self.fecha_bloqueada.id}]'