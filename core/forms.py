from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Q
from django.db.utils import IntegrityError
from django.utils.timezone import make_aware
from . import models
from .models import Usuario, Categoria, Servicio, HorarioDisponible
import datetime

class FormBase(forms.Form):
    ERROR_CLASS = (
        "invalid:border-pink-500 invalid:text-pink-600 "
        "focus:border-sky-500 focus:outline focus:outline-sky-500 "
        "focus:invalid:border-pink-500 focus:invalid:outline-pink-500 "
        "disabled:border-gray-200 disabled:bg-gray-50 disabled:text-gray-500 "
        "disabled:shadow-none dark:disabled:border-gray-700 dark:disabled:bg-gray-800/20"
    )

    def full_clean(self):
        super().full_clean()
        if not self.errors:
            return
        for name in self.errors.keys():
            if name in self.fields:
                w = self.fields[name].widget
                existing = w.attrs.get("class", "")
                if self.ERROR_CLASS not in existing:
                    w.attrs["class"] = f"{existing} {self.ERROR_CLASS}".strip()

    def show_errors(self, request):
        if not request:
            return
        for field, errors in self.errors.items():
            for error in errors:
                messages.error(request, error, extra_tags=field)
        for error in self.non_field_errors():
            messages.error(request, error, extra_tags="__all__")
        

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
        fields = ['nombre', 'apellidos', 'email', 'telefono']

    password = forms.CharField(
        label='Nueva Contraseña (Opcional)', 
        max_length=256, 
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Introduce una nueva contraseña.'
        }),
    )
    confirmar_password = forms.CharField(
        label='Confirmar nueva contraseña (Opcional)',
        max_length=256,
        required=False, 
        widget=forms.PasswordInput(attrs={
            'class': "inputLabel",
            'placeholder': 'Confirma la nueva contraseña.'
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
    categoria = forms.ModelChoiceField(
        label='Categoría:',
        queryset=Categoria.objects.filter(activa=True).order_by('nombre'),
        required=True,
        empty_label='Selecciona una categoría',
        widget=forms.Select(attrs={'class': "form-control form-control-sm shadow-sm"})
    )

    servicios = forms.ModelMultipleChoiceField(
        label='Servicios:',
        queryset=models.Servicio.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple
    )

    horario = forms.ChoiceField(
        label='Horarios disponibles: ',
        required=True,
        choices=[],
        widget=forms.Select(attrs={'class': "form-control form-control-sm shadow-sm"})
    )

    def clean_fecha_cita(self):
        fecha = self.cleaned_data.get('fecha_cita')
        fecha_hoy = datetime.datetime.now().date()
        if fecha < fecha_hoy:
            raise ValidationError('No se permite agendar citas para fechas pasadas.')
        return fecha
    
    def clean_horario(self):
        fecha = self.cleaned_data.get('fecha_cita')
        horario = self.cleaned_data.get('horario')
        if not horario:
            return horario
        if fecha:
            libres = dict(models.Cita.horarios_disponibles(fecha))
            if horario not in libres:
                raise ValidationError('Ese horario ya no está disponible para la fecha seleccionada.')
        return horario
    
    def clean_servicios(self):
        servicios = self.cleaned_data.get('servicios')
        for servicio in servicios:
            print(servicio)
        return servicios
    
    def to_cita(self):
        try:
            fulldate = f"{self.cleaned_data['fecha_cita']} {self.cleaned_data['horario']}"
            dateobj = datetime.datetime.strptime(fulldate, '%Y-%m-%d %H:%M:%S')
            cita = models.Cita()
            cita.fecha_cita = dateobj
            cita.cliente = self.cliente
            cita.fecha_creacion = datetime.datetime.now()

            cita.save()
            for serv in self.cleaned_data['servicios']:
                cita.servicios.add(serv)
            return cita
        except IntegrityError as e:
           return None

    def __init__(self, cliente: models.Usuario, *args, **kwargs):
        self.cliente = cliente
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.filter(activa=True).order_by('nombre')
        self.fields['servicios'].label_from_instance = lambda obj: f"{obj.nombre} - ${obj.precio} ({obj.categoria})"
        self.fields['horario'].choices = [('', 'Selecciona un horario')]

        cat_id = None
        data = getattr(self, 'data', None)
        if data and data.get('categoria'):
            try:
                cat_id = int(data.get('categoria'))
            except (TypeError, ValueError):
                cat_id = None
        elif self.initial.get('categoria'):
            try:
                cat_id = int(self.initial['categoria'])
            except (TypeError, ValueError):
                if isinstance(self.initial['categoria'], models.Categoria):
                    cat_id = self.initial['categoria'].id

        if cat_id:
            self.fields['servicios'].queryset = (
                models.Servicio.objects.filter(categoria_id=cat_id).order_by('nombre')
            )
        else:
            self.fields['servicios'].queryset = models.Servicio.objects.none()

        fecha_str = (data or {}).get('fecha_cita') or self.initial.get('fecha_cita')
        if fecha_str:
            import datetime as _dt
            try:
                f = _dt.datetime.strptime(str(fecha_str), '%Y-%m-%d').date()
                choices = models.Cita.horarios_disponibles(f)
                self.fields['horario'].choices = choices or [('', 'Sin horarios disponibles')]
                if data and data.get('horario'):
                    self.fields['horario'].initial = data.get('horario')
            except ValueError:
                pass

class CitasAdminForm(FormBase):
    cita: models.Cita = None
    cliente = forms.ModelChoiceField(
        label='Cliente: ',
        queryset=models.Usuario.objects.all(),
        empty_label="Selecciona un cliente",
        required=True,
        widget=forms.Select(attrs={'class': "form-control form-control-sm shadow-sm"})
    )
    fecha_cita = forms.DateField(
        label='Selecciona el día: ',
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={
            'class': "form-control form-control-sm shadow-sm",
            'type': 'date',
            'readonly': True,
        }),
    )
    categoria = forms.ModelChoiceField(
        label='Categoría:',
        queryset=Categoria.objects.filter(activa=True).order_by('nombre'),
        required=True,
        empty_label='Selecciona una categoría',
        widget=forms.Select(attrs={'class': "form-control form-control-sm shadow-sm", 'id': 'id_categoria'})
    )
    servicios = forms.ModelMultipleChoiceField(
        label='Servicios:',
        queryset=models.Servicio.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple
    )
    horario = forms.ChoiceField(
        label='Horarios disponibles: ',
        required=True,
        choices=[],
        widget=forms.Select(attrs={'class': "form-control form-control-sm shadow-sm"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['cliente'].queryset = Usuario.objects.exclude(id=1)
        self.fields['cliente'].label_from_instance = lambda obj: f"{obj.nombre} {obj.apellidos}"
        self.fields['servicios'].label_from_instance = lambda obj: f"{obj.nombre} - ${obj.precio} ({obj.categoria})"
        self.fields['horario'].choices = [('', 'Selecciona un horario')]
        cat_id = None
        data = getattr(self, 'data', None)
        if data and data.get('categoria'):
            try:
                cat_id = int(data.get('categoria'))
            except (TypeError, ValueError):
                cat_id = None
        elif self.initial.get('categoria'):
            try:
                cat_id = int(self.initial['categoria'])
            except (TypeError, ValueError):
                if isinstance(self.initial['categoria'], models.Categoria):
                    cat_id = self.initial['categoria'].id

        if cat_id:
            self.fields['servicios'].queryset = (
                models.Servicio.objects.filter(categoria_id=cat_id).order_by('nombre')
            )
        else:
            self.fields['servicios'].queryset = models.Servicio.objects.none()

        fecha_str = (data or {}).get('fecha_cita') or self.initial.get('fecha_cita')
        if fecha_str:
            import datetime as _dt
            try:
                f = _dt.datetime.strptime(str(fecha_str), '%Y-%m-%d').date()
                choices = models.Cita.horarios_disponibles(f)
                self.fields['horario'].choices = choices or [('', 'Sin horarios disponibles')]
                if data and data.get('horario'):
                    self.fields['horario'].initial = data.get('horario')
            except ValueError:
                pass

    def clean_cliente(self):
        cliente = self.cleaned_data.get('cliente')
        if cliente == "__new__":
            return None
        return cliente

    def clean_fecha_cita(self):
        fecha = self.cleaned_data.get('fecha_cita')
        if fecha and fecha < datetime.datetime.now().date():
            raise ValidationError('No se permite agendar citas para fechas pasadas.')
        return fecha

    def clean_horario(self):
        h = self.cleaned_data.get('horario')
        if not h:
            raise ValidationError('Selecciona un horario.')

        try:
            t = datetime.datetime.strptime(h, '%H:%M:%S').time() if len(h) == 8 \
                else datetime.datetime.strptime(h, '%H:%M').time()
        except ValueError:
            raise ValidationError('Formato de hora inválido.')

        fecha = self.cleaned_data.get('fecha_cita')
        if fecha:
            if models.Cita.objects.filter(fecha_cita__date=fecha,
                                        fecha_cita__time=t).exists():
                raise ValidationError('Ese horario ya está tomado.')

        self.cleaned_data['horario'] = t.strftime('%H:%M:%S')
        return self.cleaned_data['horario']

    def clean_servicios(self):
        servicios = self.cleaned_data.get('servicios')
        for servicio in servicios:
            print(servicio)
        return servicios

    def to_cita(self):
        try:
            fecha = self.cleaned_data['fecha_cita']  
            hstr  = self.cleaned_data['horario']
            try:
                t = datetime.time.fromisoformat(hstr)
            except ValueError:
                t = datetime.datetime.strptime(hstr, '%H:%M').time()

            dateobj = datetime.datetime.combine(fecha, t)

            cita = models.Cita()
            cita.fecha_cita = dateobj
            cita.cliente = getattr(self, 'cliente', None) or self.cleaned_data['cliente']
            cita.fecha_creacion = datetime.datetime.now()
            cita.save()

            for serv in self.cleaned_data['servicios']:
                cita.servicios.add(serv)

            return cita
        except IntegrityError:
            return None

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
            print(f"Se eliminará el comprobante asociado a la cita con id={self.cleaned_data['id_cita']}")
        return boolean

    def clean_comprobante(self):
        eliminar_archivo = self.cleaned_data['eliminar_archivo']
        if eliminar_archivo:
            return None

        from django.core.files.uploadedfile import InMemoryUploadedFile
        file : InMemoryUploadedFile = self.cleaned_data['comprobante']
        if file:
            file_extension = file.content_type.split('/')[1]
            file.name = f"COMPROBANTE-{self.cleaned_data['id_cita']}-{datetime.datetime.now().date()}.{file_extension}"
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
        choices=(),  # <- vacío aquí
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-check-input form-check-inline'}
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
        motivo = motivo.replace('\r', '').replace('\n', '').strip()
        if len(motivo) > 100:
            raise ValidationError(f'Asegúrese de que este valor tenga como máximo 100 caracteres (tiene {len(motivo)}).')
        return motivo

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        date = datetime.datetime.strptime(fecha, '%Y-%m-%d')
        if isinstance(date, datetime.date):
            fecha_bloqueada = models.FechaBloqueada.objects.filter(fecha = date).first()
            if not fecha_bloqueada:
                print(f'Fecha: {date} <- La fecha está disponible')
            else:
                print(f'Fecha: {date}  <- {fecha_bloqueada}')
            return date
        raise ValidationError('No se envió una fecha válida')
    
    def clean_horarios(self):
        horarios = self.cleaned_data['horarios']
        if self.cleaned_data.get('todo_el_dia'):
            self.lista_horarios = [datetime.datetime.strptime(v, '%H:%M:%S').time()
                                for v, _ in self.fields['horarios'].choices]
            return horarios

        if not horarios:
            return None

        self.lista_horarios = []
        for h in horarios:
            try:
                t = datetime.datetime.strptime(h, '%H:%M:%S').time()
                self.lista_horarios.append(t)
            except ValueError:
                raise ValidationError('Formato de hora inválido')
        return horarios
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import HorarioDisponible
        self.fields['horarios'].choices = HorarioDisponible.as_choices()


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

"""
FORMS PARA AGREGAR CATEGORÍAS Y SERVICIOS
"""

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre de la categoría'
            }),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.activa = True
        if commit:
            obj.save()
        return obj

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'precio', 'categoria']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre del servicio'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'
            }),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
        }