from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from smtplib import SMTPRecipientsRefused, SMTPException
from . import models

class Notificacion:
    def __init__(self, email, telefono, usuario : models.Usuario):
        self.email = email
        self.telefono = telefono
        self.usuario = usuario

    def enviar_confirmacion(self):
        try:# preparar contenido del email
            context = {
                'usuario': self.usuario,
                'token_url': 'puta.com',
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
