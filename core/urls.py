from django.urls import path, include
from . import views

urlpatterns = [
     path('', views.index, name='auth_index'),
     path('registro/', views.registro, name='auth_registro'),
     path('login/', views.login_view, name='auth_login'),
     path('logout/', views.logout_view, name='auth_logout'),
     path('editar-datos/', views.editar_usuario, name='auth_usuario'),
     path('citas/', views.agendar_cita, name='auth_cita'),
     path('success/', views.success, name='auth_success_view'),

     path("__reload__/", include("django_browser_reload.urls")),
]