from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from django.conf import settings
from django.urls import reverse 
from django.http.request import HttpRequest
import datetime

import os
import pandas
import time
from core import models


def generar_token(data) -> str:
    serializer = URLSafeTimedSerializer(secret_key=settings.SECRET_KEY)
    token = serializer.dumps(data, salt=settings.TOKEN_SALT)
    return token



def verificar_token(token, expiration_secs : int = 86400): # 60secs * 60min * 24hrs
    try:
        serializer = URLSafeTimedSerializer(secret_key=settings.SECRET_KEY)
        data = serializer.loads(token, salt=settings.TOKEN_SALT, max_age=expiration_secs)
        return data, False
    except SignatureExpired as e:
        print(f'Token expirado: {type(e)} {str(e)}')
        return None, True
    except Exception as e:
        return None, False  

def token_to_url(token, request : HttpRequest) -> str:
    partial_url = reverse('auth_verify') + f'token=?{token}'
    full_url = request.build_absolute_uri(partial_url)
    return full_url


def to_unix_timestamp(fecha) -> int:
    if isinstance(fecha, datetime.date):
        return int(time.mktime(fecha.timetuple())) * 1000
    return int(time.mktime(fecha.date().timetuple())) * 1000

"""
PARA PARSEAR Y GENERAR LOS SERVICIOS A PARTIR DEL EXCEL
"""
def process_excel():
    path = f'{os.getcwd()}/booknails/static/files/'
    filepath = f'{path}/Servicios.xlsx'
    excel = pandas.read_excel(filepath)
    for index, row in excel.iterrows():
        servicio = models.Servicio(**row.to_dict())
        if not models.Servicio.objects.filter(nombre=servicio.nombre, precio=servicio.precio, categoria=servicio.categoria).exists():
            if row['categoria'] in dict(models.Servicio.Categorias.choices):
                servicio.save()
                print(f'[{index<2}] creado {servicio}')