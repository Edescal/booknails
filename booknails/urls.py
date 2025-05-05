from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    
    path('index/', views.menu, name='menu'),
    # path('login/', auth_views.LoginView.as_view(template_name='auth_login'), name='login'),
    # path('admin/', admin.site.urls),

    path('auth/', include('core.urls')),
    path('api/', include('api.urls')),
    path('users/', include('users.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)