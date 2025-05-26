from django.urls import path, include
from . import views


urlpatterns = [
    # esta está para quitarse porque no parece haber sido útil
    # esta también
    path('calendario/', views.calendario_admin, name='calendario'),

    path('agendar-cita/', views.agendar_cita, name='agendar_cita'),
    path('agendar-super/', views.agendar_super, name='agendar_super'),

    path('registro-y-cita/', views.registro_y_cita, name='registro_y_cita'),
    path('eliminar-cita/', views.eliminar_cita, name='eliminar_cita'),
    path('editar-citas/', views.editar_cita, name='editar_citas'),
    # este es un POST para actualizar el comprobante de pago
    path('editar-archivo-cita/', views.actualizar_comprobante, name='cita_comprobante'),

    path('mis-citas/', views.ver_citas_usuarios, name='ver_mis_citas'),
    
    # falta otra para que la dueña vea la agenda
    path('agenda/', views.ver_agenda_inicio, name='ver_agenda'),
    path('agenda/<int:año>/<int:mes>', views.ver_agenda, name='ver_agenda_redirect'),
    
    path('bloquear-fecha/', views.bloquear_fecha, name='bloquear_fechas_get'),
    path('bloquear-fecha/eliminar', views.eliminar_fecha_bloqueada, name='testeando_eliminar'),

] 