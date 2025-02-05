from django.urls import path
from . import views

urlpatterns = [
     path('', views.index, name='webapp_index'),
     path('registro/', views.registro, name='webapp_registro'),
     path('login/', views.login, name='webapp_login')
]