from django.urls import path, include
from . import views

urlpatterns = [
     path('citas/<int:año>/<int:mes>/<int:dia>', views.api_get_citas, name='API_get_citas'),
     path('users/', views.api_get_usuarios, name='API_get_usuarios'),
     path('servicios/', views.api_get_servicios, name='API_get_servicios'),
     path('servicios/<str:categoria>', views.api_get_servicios_cat, name='API_get_servicios_categoria'),

     path('fecha-bloqueada/<int:año>/<int:mes>/<int:dia>', views.api_is_fecha_bloqueada, name='API_get_fecha_bloq'),
     path('fechas-bloqueadas/<int:año>/<int:mes>', views.api_fechas_bloqueadas_mes, name='API_get_fecha_bloq'),

     path('mes-bloqueado/<int:año>/<int:mes>', views.api_mes_completamente_bloqueado, name='API_bool_mes_bloqueado'),
     
     path('horarios/<int:year>/<int:mes>/<int:dia>', views.api_get_horarios, name='API_get_horarios'),

     path('horarios_servicio_disponibles/<int:id_servicio>/<int:año>/<int:mes>/<int:dia>', views.horario__disponible_servicio, name='API_horarios_servicio'),
]


