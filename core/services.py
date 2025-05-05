from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.conf import settings
from smtplib import SMTPRecipientsRefused, SMTPException
from . import models
from api import serializers

from cryptography.fernet import Fernet

import secrets, logging

# key = Fernet.generate_key()
# print(key)

fernet = Fernet(b'LgSAckJzkYiTVkvdI5JuoUlRCIlw9b4JOa4HCOwuBHs=')

class Notificacion:
    def __init__(self, usuario : models.Usuario):
        self.usuario = usuario

    def _validar_email(self):
        try:
            validate_email(self.usuario.email)
            return True
        except ValidationError:
            return False

    def _enviar_email(self, to : list[str], subject : str, content : str) -> bool:
        email = EmailMessage(
            from_email=settings.EMAIL_HOST_USER,
            subject=subject,
            body=content,
            to=to,
        )
        email.content_subtype = 'html'
        try:
            enviado : int = email.send(fail_silently=False)
            if enviado == 0:
                logging.error('No se pudo enviar el correo')
            return True
        except (SMTPRecipientsRefused, SMTPException) as e:
            logging.error(f'Error al enviar correo a: {to}: {str(e)}')
        return False
    
    def _render_email(self, context = None) -> str:
        if not context:
            context = {
                'usuario': self.usuario,
            }
        return render_to_string('emails/email_confirmacion.html', context)

    def enviar_confirmacion(self, cita : models.Cita):
        if self.usuario.is_anonymous:
            logging.error(f'El usuario no está autenticado')
            return False

        if not self.usuario.id == cita.cliente.id:
            logging.error(f'La cita no pertenece a {self.usuario.get_full_name()}')
            return False

        if not self._validar_email():
            logging.error(f'El email no es válido: {self.usuario.email}')
            return False
        
        context = {
            'usuario': self.usuario,
            'cita': cita,
        }
        return self._enviar_email(
            to=[self.usuario.email],
            subject='Confirmación de cita',
            content=self._render_email(context),
        )

    def __repr__(self):
        if self.usuario.is_anonymous:
            return f"Notificacion (usuario={self.usuario})"
        return f"Notificacion (usuario='{self.usuario.get_full_name()}' & email='{self.usuario.email}')"


class LoginVerify:
    def __init__(self, id = None, usuario:models.Usuario = None):
        if id:
            self.id = id
        else: self.id = secrets.token_hex(4).upper()        
        if isinstance(usuario, dict):
            self.usuario = models.Usuario.objects.get(id=usuario.get('id'))
        else: self.usuario = usuario

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "usuario": serializers.UsuarioSerializer(self.usuario).data,
        }
    

