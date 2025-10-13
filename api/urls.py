from django.urls import path, include
from django.urls import re_path
from . import views
from .views import api_get_horarios

urlpatterns = [
     path('citas/<int:año>/<int:mes>/<int:dia>', views.api_get_citas, name='API_get_citas'),
     path('users/', views.api_get_usuarios, name='API_get_usuarios'),
     path('servicios/', views.api_get_servicios, name='API_get_servicios'),
     path('servicios/<str:categoria>', views.api_get_servicios_cat, name='API_get_servicios_categoria'),
     path('fecha-bloqueada/<int:año>/<int:mes>/<int:dia>', views.api_is_fecha_bloqueada, name='API_get_fecha_bloq'),
     path('fechas-bloqueadas/<int:año>/<int:mes>', views.api_fechas_bloqueadas_mes, name='API_get_fecha_bloq'),
     path('mes-bloqueado/<int:año>/<int:mes>', views.api_mes_completamente_bloqueado, name='API_bool_mes_bloqueado'),     
     re_path(r"^horarios/(?P<year>\d{4})/(?P<mes>\d{1,2})/(?P<dia>\d{1,2})/?$", api_get_horarios, name="api_get_horarios"),
     path('admin/<str:kind>/', views.admin_list, name='admin_list'),
     path('admin/<str:kind>/<int:pk>/', views.admin_update, name='admin_update'),
     path('admin/<str:kind>/<int:pk>/delete/', views.admin_delete, name='admin_delete'),
]