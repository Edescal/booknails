from django.urls import path, include
from . import views

urlpatterns = [
     path('', views.index, name='auth_index'),
     path('registro/', views.registro, name='auth_registro'),
     path('login/', views.login_view, name='auth_login'),
     path('logout/', views.logout_view, name='auth_logout'),

     path('citas/', views.agendar_cita, name='auth_cita'),
     path('success/', views.success, name='auth_success_view'),


     path('api/citas/', views.api_get_citas, name='API_get_citas'),
     path('api/users/', views.api_get_usuarios, name='API_get_usuarios'),
     path('api/servicios/', views.api_get_servicios, name='API_get_servicios'),
     path('api/fechas_bloq/', views.api_get_fechas_bloqueadas, name='API_get_fechas_bloq'),
     path('api/fechas_bloq/<int:mes>/', views.api_get_fechas_mes, name='API_get_fechas_bloq'),


     path("__reload__/", include("django_browser_reload.urls")),
]