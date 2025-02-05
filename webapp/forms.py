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
                field.widget.attrs.update({'class': field.widget.attrs.get('class', '') + ' is-invalid'})
                
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
            'class': "form-control shadow",
            'placeholder': 'Introduce tu usuario'
        }),
    )
    password = forms.CharField(
        label='contraseña', 
        max_length=256, 
        widget=forms.PasswordInput(attrs={
            'class': "form-control shadow",
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
            query = (Q(username__icontains=credential) | Q(email__icontains=credential)) & Q(password__contains=password)
            user = models.Usuario.objects.filter(query).first()
            if user is None:
                raise ValidationError('Contraseña equivocada')
        return password

    def get_user(self):
        credential = self.cleaned_data.get('credential', None)
        password = self.cleaned_data.get('password', None)
        if credential and password:
            query = (Q(username__icontains=credential) | Q(email__icontains=credential)) & Q(password__contains=password)
            return models.Usuario.objects.filter(query).first()
        return None


class CitasForm(FormBase):
    

    pass


