from django.urls import path, include
from . import views

urlpatterns = [
     path('', views.index, name='auth_index'),
     path('registro/', views.registro, name='auth_registro'),
     path('login/', views.login_view, name='auth_login'),
     path('agendar/', views.agendar_cita, name='auth_cita'),
     path('success/', views.success, name='auth_success_view'),
     path("__reload__/", include("django_browser_reload.urls")),
]