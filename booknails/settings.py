"""
Django settings for booknails project.
"""

from pathlib import Path
import dj_database_url
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-32yx!$o!cyuvo*wz#ofn3^u*_(2&&uyjpe4iq1!i36vb9!m3=r')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(' ')
# ['127.0.0.1', '192.168.0.14']

# Custom model
AUTH_USER_MODEL = 'core.Usuario'

AUTHENTICATION_BACKENDS = [
    # "django.contrib.auth.backends.ModelBackend",
    'core.authentication_backends.UsuarioBackend',
]

# SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
# SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Usa base de datos para sesiones
SESSION_COOKIE_SECURE = False  # Debe ser False en desarrollo
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # No cerrar sesión al cerrar el navegador
SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Usar base de datos para sesiones
SESSION_COOKIE_AGE = 43200  # 12 horas en segundos
SESSION_SAVE_EVERY_REQUEST = True  # Forzar que Django guarde la sesión en cada request

X_FRAME_OPTIONS = 'SAMEORIGIN'


TOKEN_SALT='a9z834xz'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'api',
    'tailwind',
    'theme',
    'django_browser_reload',
    'rest_framework',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO', 
    },
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.BrowsableAPIRenderer',  # HTML 
        'rest_framework.renderers.StaticHTMLRenderer',  # HTML 
        'rest_framework.renderers.JSONRenderer',  # Solo responde en formato JSON
    ]
}

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Emails
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "eduardo1582000@gmail.com"
EMAIL_HOST_PASSWORD = "jzff xmsn ebrc hwnu"  # Usa una contraseña de aplicación en Gmail
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


TAILWIND_APP_NAME = 'theme'

INTERNAL_IPS = [
    "127.0.0.1"
]

NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware",
        'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'booknails.urls'

LOGIN_URL = 'auth_login'
LOGIN_REDIRECT_URL = 'auth_success'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'booknails.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# postgresql://booknails_user:SDgulDgRr2XJ8e91RTXgJnaoCLfosyFO@dpg-d0mh55je5dus738h22ag-a.oregon-postgres.render.com/booknails

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'alt': {
        'ENGINE': 'django.db.backends.mysql',  # Usar el backend de MySQL
        'NAME': 'booknails',  # Nombre de la base de datos
        'USER': 'root',                  # Usuario de MariaDB
        'PASSWORD': 'admin123',           # Contraseña de MariaDB
        'HOST': 'localhost',                   # Host de la base de datos
        'PORT': '3306',                        # Puerto de MariaDB (por defecto es 3306)
        'OPTIONS': {
            # 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",  # Modo SQL estricto
            'init_command': "SET default_storage_engine=INNODB;"  # Modo SQL estricto
        },
    }
}

database_url = os.environ.get('DATABASE_URL')
DATABASES['default'] = dj_database_url.parse(database_url)


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'  # O tu zona horaria

USE_I18N = True
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# STATIC_URL = 'static/'

# STATIC_ROOT  = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'   # Carpeta donde Django va a colectar todos los estáticos para producción

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'booknails/static'), 
]
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
