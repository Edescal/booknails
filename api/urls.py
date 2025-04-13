from django.urls import path, include
from . import views

urlpatterns = [
     path('citas/<int:año>/<int:mes>', views.api_get_citas, name='API_get_citas'),
     path('users/', views.api_get_usuarios, name='API_get_usuarios'),
     path('servicios/', views.api_get_servicios, name='API_get_servicios'),
     path('servicios/<str:categoria>', views.api_get_servicios_cat, name='API_get_servicios_categoria'),
     path('fechas_bloq/', views.api_get_fechas_bloqueadas, name='API_get_fechas_bloq'),
]


