from django.urls import path, include
from . import views

urlpatterns = [
     path('', views.index, name='webapp_index'),
     path('registro/', views.registro, name='webapp_registro'),
     path('login/', views.login, name='webapp_login'),
     path('agendar/', views.agendar_cita, name='webapp_cita'),
     path('success/', views.success, name='success_view'),
     path("__reload__/", include("django_browser_reload.urls")),
]