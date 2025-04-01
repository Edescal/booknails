from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Q
from django.db.utils import IntegrityError
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
<<<<<<< HEAD
            'class': "inputLabel",
=======
            'class': "labelReg",
>>>>>>> fdb1a1bb11891936c3c05b9242a844252fb624cc
            'placeholder': 'Introduce una nueva contraseña (opcional)'
        }),
    )
    confirmar_password = forms.CharField(
        label='Confirmar nueva contraseña',
        max_length=256,
        required=False,  # Solo si se pidió una nueva contraseña
        widget=forms.PasswordInput(attrs={
<<<<<<< HEAD
            'class': "inputLabel",
=======
            'class': "labelReg",
>>>>>>> fdb1a1bb11891936c3c05b9242a844252fb624cc
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
    cliente : models.Usuario = None
    fecha_cita = forms.DateField(
        label='Selecciona el día: ',
        input_formats=['%Y-%m-%d', '%d-%m-%Y'],
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={
            'class': "form-control shadow-sm",
            'placeholder': 'Introduce tu contraseña',
            'type': 'date',
            'readonly': True,
        }),
    )
    hora_cita = forms.TimeField(
        label='Horarios disponibles: ',
        input_formats=['%H:%M'],
        required=True,
        widget=forms.DateInput(
            format="%Y-%m-%d", 
            attrs={
                "type": "time", 
                'class': "form-control shadow-sm",
            }
        ),
    )
    categoria = forms.ChoiceField(
        label='Categoría',
        choices=models.Servicio.Categorias.choices,
        required=True,
        widget=forms.Select(
            attrs={'class': "form-control shadow-sm",}
        )
    )
    servicios = forms.ModelMultipleChoiceField(
        label='Servicios',
        queryset=models.Servicio.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple
    )
    # servicios = forms.MultipleChoiceField(
    #     label='Servicios',
    #     choices=models.Servicio.objects.none(),
    #     initial=None,
    #     required=True,
    #     widget=forms.CheckboxSelectMultiple
    # )

    def clean_fecha_cita(self):
        fecha = self.cleaned_data.get('fecha_cita')
        return fecha
    
    def clean_hora_cita(self):
        hora = self.cleaned_data.get('hora_cita')
        return hora
    
    def clean_servicios(self):
        servicios = self.cleaned_data.get('servicios')

        """VALIDAR Y CONVERTIR A UNA INSTANCIA VERDADERA"""
        print(servicios)
        for s in servicios:
            print(f'SERVICIO: {s}')
        
        """^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"""
        return servicios
    
    def to_cita(self):
        try:
            fulldate = f'{self.cleaned_data['fecha_cita']} {self.cleaned_data['hora_cita']}'
            dateobj = datetime.datetime.strptime(fulldate, '%Y-%m-%d %H:%M:%S')
            cita = models.Cita()
            cita.fecha_cita = dateobj
            cita.cliente = self.cliente
            cita.fecha_creacion = datetime.datetime.now()
            cita.save()
            for serv in self.cleaned_data['servicios']:
                cita.servicios.add(serv)
                print(f'add servicio: {serv}')
            return cita
        except IntegrityError as e:
           return None



    def __init__(self, cliente : models.Usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cliente:
            self.cliente = cliente
        # self.fields['servicios'].queryset = models.Servicio.objects.none()

