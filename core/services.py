from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from smtplib import SMTPRecipientsRefused, SMTPException
from . import models
from api import serializers

from cryptography.fernet import Fernet

import secrets

# key = Fernet.generate_key()
# print(key)

fernet = Fernet(b'LgSAckJzkYiTVkvdI5JuoUlRCIlw9b4JOa4HCOwuBHs=')

class Notificacion:
    def __init__(self, email, telefono, usuario : models.Usuario):
        self.email = email
        self.telefono = telefono
        self.usuario = usuario

    def enviar_confirmacion(self):
        try:# preparar contenido del email
            context = {
                'usuario': self.usuario,
                'token_url': 'jkjkjkj.com',
            }
            content = render_to_string('emails/email_confirmacion.html', context)
            # crear email
            email = EmailMessage(
                subject='Confirmación de cuenta en Nails by Marin',
                from_email=settings.EMAIL_HOST_USER,
                to=[self.usuario.email],
                body=content,
            )
            email.content_subtype = 'html'
            sended : int = email.send(fail_silently=False)
            if sended == 0:
                print(f'[SATANIC_ERROR]: No email sended!')
        except SMTPRecipientsRefused as e:
            print(str(e))
        except SMTPException as e:
            print(str(e))

    def enviar_recordatorio(self):
        pass


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
    

