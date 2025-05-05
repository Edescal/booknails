from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Q
from django.db.utils import IntegrityError
from django.utils.timezone import make_aware
from . import models
from .models import Usuario
import datetime

class FormBase(forms.Form):
    def __init__(self, *args, **kwargs):
        # primero se instancia el objeto base
        super().__init__(*args, **kwargs)
        # luego, si hay errores, configurar las clases
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update({'class': field.widget.attrs.get('class', '') + ' invalid:border-pink-500 invalid:text-pink-600 focus:border-sky-500 focus:outline focus:outline-sky-500 focus:invalid:border-pink-500 focus:invalid:outline-pink-500 disabled:border-gray-200 disabled:bg-gray-50 disabled:text-gray-500 disabled:shadow-none dark:disabled:border-gray-700 dark:disabled:bg-gray-800/20'})
                
    def show_errors(self, request):
        print('Errores del formulario')
        for field, errors in self.errors.items():
            for error in errors:
                print(f'Error: {error}\tField: {field}')
                if request:
                    messages.error(request=request, message=error, extra_tags=field)
        

class RegistroForm(FormBase):
    nombre = forms.CharField(
        max_length=20,
        label='',
        required=True, 
        widget=forms.TextInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Nombre(s)'
        }),
    )
    apellidos = forms.CharField(
        max_length=50,
        label='',
        required=False, 
        widget=forms.TextInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Apellidos'
        }),
    )
    usuario = forms.CharField(
        max_length=20, 
        label='',
        required=True, 
        widget=forms.TextInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Usuario'
        }),
    )
    email = forms.EmailField(
        max_length=256,
        label='',
        widget=forms.TextInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Correo Electronico'
        }),
    )
    telefono = forms.CharField(
        max_length=10,
        label='',
        widget=forms.TextInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Teléfono'
        }),
    )
    password = forms.CharField(
        label='',
        max_length=256, 
        widget=forms.PasswordInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Contraseña'
        }),
    )
    confirmar_password = forms.CharField( 
        max_length=255, 
        label='',
        widget=forms.PasswordInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Confirmar Contraseña'
        }),
    )

    def clean_usuario(self):
        username = self.cleaned_data.get('usuario')
        usuario = models.Usuario.objects.filter(username=username).first()
        if usuario:
            raise ValidationError('Este nombre de usuario ya existe.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        usuario = models.Usuario.objects.filter(email=email)
        if usuario:
            raise ValidationError('Este email ya está registrado.')
        return email
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        usuario = models.Usuario.objects.filter(telefono=telefono)
        if usuario:
            raise ValidationError('Este teléfono ya está registrado')
        return telefono

    def clean_confirmar_password(self):
        confirmation = self.cleaned_data.get('confirmar_password')
        password = self.cleaned_data.get('password')
        if password != confirmation:
            raise ValidationError('Las contraseñas no coinciden. Vuelve a intentarlo.')
        return confirmation

class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellidos', 'email', 'telefono']  # Campos que quieres permitir editar

    password = forms.CharField(
        label='Nueva Contraseña', 
        max_length=256, 
        required=False,  # Solo lo pedimos si el usuario desea cambiar la contraseña
        widget=forms.PasswordInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Introduce una nueva contraseña (opcional)'
        }),
    )
    confirmar_password = forms.CharField(
        label='Confirmar nueva contraseña',
        max_length=256,
        required=False,  # Solo si se pidió una nueva contraseña
        widget=forms.PasswordInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Confirma la nueva contraseña (opcional)'
        }),
    )

class LoginForm(FormBase):
    credential = forms.CharField( 
        max_length=256,
        label='',
        widget=forms.TextInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Usuario/Correo'
        }),
    )
    password = forms.CharField(
        max_length=256, 
        label='',
        widget=forms.PasswordInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Contraseña'
        }),
    )

    def clean_credential(self):
        credential = self.cleaned_data['credential']
        query = Q(username__icontains=credential) | Q(email__icontains=credential)
        user = models.Usuario.objects.filter(query).first()
        if user == None:
            raise ValidationError('No se encontró ningún usuario')
        return credential

    def clean_password(self):
        password = self.cleaned_data['password']
        credential = self.cleaned_data.get('credential', None)
        if credential:
            query = Q(username__icontains=credential) | Q(email__icontains=credential)
            user = models.Usuario.objects.filter(query).first()
            if not user:            
                raise ValidationError('No se encontró ningún usuario')  
            if not user.check_password(password):
                raise ValidationError('Contraseña equivocada')
        return password

    def get_user(self):
        credential = self.cleaned_data.get('credential', None)
        password = self.cleaned_data.get('password', None)
        if credential and password:
            query = Q(username__icontains=credential) | Q(email__icontains=credential)
            return models.Usuario.objects.filter(query).first()
        return None


class CitasForm(FormBase):
    cita : models.Cita = None
    cliente : models.Usuario = None
    fecha_cita = forms.DateField(
        label='Selecciona el día: ',
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={
            'class': "form-control form-control-sm shadow-sm",
            'placeholder': 'Introduce tu contraseña',
            'type': 'date',
            'readonly': True,
        }),
    )
    categoria = forms.ChoiceField(
        label='Categoría',
        choices=models.Servicio.Categorias.choices,
        required=True,
        widget=forms.Select(
            attrs={'class': "form-control form-control-sm shadow-sm",}
        )
    )
    servicios = forms.ModelMultipleChoiceField(
        label='Servicios',
        queryset= models.Servicio.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple
    )
    horario = forms.ChoiceField(
        label= 'Horarios disponibles: ',
        required=False,
        choices=cita.hora if cita else models.Horario.choices,
        widget=forms.Select(
            attrs={
                'class': "form-control form-control-sm shadow-sm",
                # 'disabled':True,
            }
        )
    )

    def clean_fecha_cita(self):
        fecha = self.cleaned_data.get('fecha_cita')
        fecha_hoy = datetime.datetime.now().date()
        if fecha > fecha_hoy:
            raise ValidationError('No se permite agendar citas para fechas pasadas.')
        return fecha
    
    def clean_horario(self):
        fecha = self.cleaned_data.get('fecha_cita')
        horario = self.cleaned_data.get('horario')
        if self.cliente:
            duplicated = models.Cita.objects.filter(
                cliente=self.cliente, 
                fecha_cita__date=fecha,
                fecha_cita__time=horario
            ).exists()
            if duplicated:
                raise ValidationError('Ya hay una cita para ese mismo día y horario.')
        return horario
    
    def clean_servicios(self):
        servicios = self.cleaned_data.get('servicios')
        for servicio in servicios:
            print(servicio)
        return servicios
    
    def to_cita(self):
        try:
            fulldate = f'{self.cleaned_data['fecha_cita']} {self.cleaned_data['horario']}'
            dateobj = datetime.datetime.strptime(fulldate, '%Y-%m-%d %H:%M:%S')
            cita = models.Cita()
            cita.fecha_cita = make_aware(dateobj)
            cita.cliente = self.cliente
            cita.fecha_creacion = make_aware(datetime.datetime.now())

            cita.save()
            for serv in self.cleaned_data['servicios']:
                cita.servicios.add(serv)

            return cita
        except IntegrityError as e:
           return None

    def __init__(self, cliente : models.Usuario, *args, **kwargs):
        self.cliente = cliente
        super().__init__(*args, **kwargs)


class ComprobanteForm(FormBase):
    id_cita = forms.IntegerField(
        required=True,
        widget= forms.HiddenInput(
            attrs= {

            }
        ),
    )
    eliminar_archivo = forms.BooleanField(
        label='Eliminar archivo adjunto',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input form-check-inline',
                'novalidate':True,
                'autocomplete': 'off',
            }
        )
    )
    comprobante = forms.FileField(
        label='Comprobante de pago de anticipo',
        required=False,
        allow_empty_file= False,
        widget=forms.FileInput(
            attrs= {
                'class': 'form-control',
            }
        )
    )

    def clean_eliminar_archivo(self):
        boolean = self.cleaned_data['eliminar_archivo']
        if boolean:
            print(f'Se eliminará el comprobante asociado a la cita con id={self.cleaned_data['id_cita']}')
        return boolean

    def clean_comprobante(self):
        eliminar_archivo = self.cleaned_data['eliminar_archivo']
        if eliminar_archivo:
            return None

        from django.core.files.uploadedfile import InMemoryUploadedFile
        file : InMemoryUploadedFile = self.cleaned_data['comprobante']
        if file:
            file_extension = file.content_type.split('/')[1]
            file.name = f'COMPROBANTE-{self.cleaned_data['id_cita']}-{datetime.datetime.now().date()}.{file_extension}'
            print(f'Save as: {file.name}')
            extensiones_permitidas = [
                'application/pdf',
                'image/jpeg',
                'image/png',
                'image/webp',
            ]
            if file.content_type not in extensiones_permitidas:
                raise ValidationError('Tipos de archivo permitidos: [PDF, JPEG, JPG, PNG, WEBP]') 
            return file
        raise ValidationError('No se envió ningún archivo')


"""
ESTOS FORMS SON PARA BLOQUEAR DIAS O RANGOS DE DÍAS
"""
class BloquearFechaForm(FormBase):
    fecha = forms.CharField(
        label='Fecha(s) que deseas bloquear',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-sm',
                'type':'date',
                'placeholder': 'fecha que quieres bloquear',
                'novalidate':True,
                'autocomplete': 'off',
            }
        ),
    )
    todo_el_dia = forms.BooleanField(
        label='Bloquear dia completo',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input form-check-inline',
                'placeholder': 'fecha que quieres bloquear',
                'novalidate':True,
                'autocomplete': 'off',
            }
        )
    )
    horarios = forms.MultipleChoiceField(
        label='Bloquear horarios específicos',
        required=False,
        choices=models.Horario.choices,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class': 'form-check-input form-check-inline',
                'placeholder': 'fecha que quieres bloquear',
                'novalidate':True,
                'autocomplete': 'off',
            }
        )
    )
    motivo = forms.CharField(
        label= 'Motivo (opcional):',
        required=False,
        widget=forms.Textarea(
            attrs= {
                'class': 'form-control form-control-sm',
                'rows': 2,
                'maxlength':100,
                'wrap':'hard',
                'style': 'resize: none;',
                'placeholder': 'Descripción de por qué quieres bloquear esta fecha',
            }
        )
    )
    lista_horarios = []
    
    def clean_motivo(self):
        motivo : str = self.cleaned_data['motivo']
        # reemplazar los saltos de línea y quitar espacios
        motivo = motivo.replace('\r', '').replace('\n', '').strip()
        # validar longitud máxima
        if len(motivo) > 100:
            raise ValidationError(f'Asegúrese de que este valor tenga como máximo 100 caracteres (tiene {len(motivo)}).')
        return motivo

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        # parsear string a fecha
        date = datetime.datetime.strptime(fecha, '%Y-%m-%d')
        # si se parseó correctamente...
        if isinstance(date, datetime.date):
            # buscar coincidencias en la BD
            fecha_bloqueada = models.FechaBloqueada.objects.filter(fecha = date).first()
            if not fecha_bloqueada:
                print(f'Fecha: {date} <- La fecha está disponible')
            else:
                print(f'Fecha: {date}  <- {fecha_bloqueada}')
            return date
        raise ValidationError('No se envió una fecha válida')
    
    def clean_horarios(self):
        horarios = self.cleaned_data['horarios']
        if not horarios:
            return None
        
        # si se eligió todo el día, no hace falta hacer nada
        if self.cleaned_data['todo_el_dia']:
            self.lista_horarios = models.Horario.values
            return horarios
        
        # si no se eligió todo el día, y tampoco se eligió un horario: error
        if len(horarios) == 0:
            raise ValidationError('Selecciona al menos un horario')

        # por cada horario elegido...
        for h in horarios:
            # convertir a fecha (y quedarse con la hora datetime.time())
            hora = datetime.datetime.strptime(h, '%H:%M:%S')
            if isinstance(hora, datetime.datetime):
                # ver si existe en los horarios preestablecidos
                if hora.time() in models.Horario.values:
                    # añadir la hora a la lista del formulario
                    print(f'Validado: {h}')
                    # asegurar que no se repite una misma hora
                    if not hora.time() in self.lista_horarios:
                        self.lista_horarios.append(hora.time())
        return horarios


class BloquearRangoForm(FormBase):
    fecha_inferior = forms.DateField(
        label='Desde:',
        required=True,
        widget=forms.DateInput(
           attrs={
                'class': 'form-control form-control-sm',
                'type':'date',
                'placeholder': 'fecha que quieres bloquear',
                'novalidate':True,
                'autocomplete': 'off',
            } 
        )    
    )
    fecha_superior = forms.DateField(
        label='Hasta:',
        required=True,
        widget=forms.DateInput(
           attrs={
                'class': 'form-control form-control-sm',
                'type':'date',
                'placeholder': 'fecha que quieres bloquear',
                'novalidate':True,
                'autocomplete': 'off',
            } 
        )    
    )
    motivo = forms.CharField(
        label= 'Motivo (opcional):',
        required=False,
        widget=forms.Textarea(
            attrs= {
                'class': 'form-control form-control-sm',
                'rows': 2,
                'maxlength':100,
                'wrap':'hard',
                'style': 'resize: none;',
                'placeholder': 'Esta descripción se compartirá para todas las fechas del mes.',
            }
        )
    )
    
    def clean(self):
        cleaned_data = super().clean()

        fecha_inf : datetime.date = cleaned_data.get('fecha_inferior', None)
        fecha_sup : datetime.date = cleaned_data.get('fecha_superior', None)

        if not (fecha_sup and fecha_inf):
            raise ValidationError('No es válido este formulario.')

        if fecha_inf > fecha_sup:
            raise ValidationError('La segunda fecha debe ser posterior a la primera.')






