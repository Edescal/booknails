from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Q

from . import models

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
        label='Nombre(s)',
        max_length=20,
        required=True, 
        widget=forms.TextInput(attrs={
            'class': "form-control shadow",
            'placeholder': 'Introduce tu contraseña'
        }),
    )
    primer_apellido = forms.CharField(
        label='Primer apellido',
        max_length=20,
        required=True, 
        widget=forms.TextInput(attrs={
            'class': "form-control shadow",
            'placeholder': 'Introduce tu contraseña'
        }),
    )
    segundo_apellido = forms.CharField(
        label='Segundo apellido',
        max_length=20,
        required=False, 
        widget=forms.TextInput(attrs={
            'class': "form-control shadow",
            'placeholder': 'Introduce tu contraseña'
        }),
    )
    usuario = forms.CharField(
        label='Nombre de usuario',
        max_length=20, 
        required=True, 
        widget=forms.TextInput(attrs={
            'class': "form-control shadow",
            'placeholder': 'Introduce tu contraseña'
        }),
    )
    email = forms.EmailField(
        label='Correo electrónico', 
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': "form-control shadow",
            'placeholder': 'Introduce tu contraseña'
        }),
    )
    telefono = forms.CharField(
        label='Telefono', 
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': "form-control shadow",
            'placeholder': 'Introduce tu contraseña'
        }),
    )
    password = forms.CharField(
        label='Contraseña', 
        max_length=256, 
        widget=forms.PasswordInput(attrs={
            'class': "form-control shadow",
            'placeholder': 'Introduce tu contraseña'
        }),
    )
    confirmar_password = forms.CharField(
        label='Confirmar contraseña', 
        max_length=255, 
        widget=forms.PasswordInput(attrs={
            'class': "form-control shadow",
            'placeholder': 'Introduce tu contraseña'
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


class LoginForm(FormBase):
    credential = forms.CharField(
        label='Usuario o correo', 
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': "block w-full rounded-xl bg-white px-3 py-2 text-base text-gray-900 outline outline-2 -outline-offset-2 outline-gray-200 placeholder:text-gray-600 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/4",
            'placeholder': 'Introduce tu usuario'
        }),
    )
    password = forms.CharField(
        label='Contraseña', 
        max_length=256, 
        widget=forms.PasswordInput(attrs={
            'class': "block w-full rounded-xl bg-white px-3 py-2 text-base text-gray-900 outline outline-2 -outline-offset-2 outline-gray-200 placeholder:text-gray-600 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/4",
            'placeholder': 'Introduce tu contraseña'
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
        input_formats=['%d/%d/%y'],
        widget=forms.DateInput(format="%Y-%m-%d", attrs={
            'class': "form-control shadow",
            'placeholder': 'Introduce tu contraseña',
            'type': 'date'
        }),
    )
    hora_cita = forms.TimeField(
        label='Selecciona la hora: ',
        input_formats=['%H:%M'],
        widget=forms.DateInput(
            format="%Y-%m-%d", 
            attrs={"type": "time"}
        ),
    )

    def __init__(self, cliente : models.Usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cliente:
            self.cliente = cliente
