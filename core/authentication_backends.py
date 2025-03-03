from django.contrib.auth.backends import BaseBackend
from django.db.models import Q
from . import models

class UsuarioBackend(BaseBackend):
    def get_user(self, user_id):
        try:
            return models.Usuario.objects.get(id=user_id)
        except models.Usuario.DoesNotExist:
            return None

    def authenticate(self, request, **kwargs):
        if request.method != 'POST':
            print(f'Método HTTP equivocado')
            return None

        username = kwargs.get('username', '')
        email = kwargs.get('email', '')
        password = kwargs.get('password', '')
        if (username or email) and password:
            try:
                query = Q(username__icontains=username) | Q(email__icontains=email)
                user = models.Usuario.objects.filter(query).first()
                if user:
                    if user.check_password(password):   
                        print(f'Se autenticó un usuario: {user}')
                        return user
                    else:
                        print('Contraseña incorrecta')
                        return None
                raise models.Usuario.DoesNotExist()
            except models.Usuario.DoesNotExist:
                print(f'No existe el usuario proporcionado')
                return None
        print('Datos insuficientes')
        return None
