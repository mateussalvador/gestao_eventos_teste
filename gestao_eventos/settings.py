import os
from pathlib import Path

from decouple import config, Csv # Para variáveis de ambiente

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY') # chave secreta via variável de ambiente
DEBUG = config('DEBUG', default=True, cast=bool) # modo debug via variável de ambiente
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv()) # hosts permitidos via variável de ambiente

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Bibliotecas de Terceiros (Conforme PDF 06 e 07)
    'rest_framework',
    'rest_framework.authtoken',  # Adicionado para Autenticação por Token [cite: 698]
    'django_filters',            # Adicionado para Filtros [cite: 918]
    'drf_spectacular',
    'corsheaders', # Para CORS se necessário
    'safedelete', # Para deleção segura de objetos

    # Minha App
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Se necessário para CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gestao_eventos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'gestao_eventos.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'core.Participante'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURAÇÃO DRF (Alinhada com PDF 06 e 07) ---
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    # Autenticação: Token para API, Session para Admin/Browser [cite: 700]
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication', 
    ],
    
    # Permissões: Leitura pública, escrita autenticada 
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    
    # Filtros Globais [cite: 929]
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    'DEFAULT_PAGINATION_CLASS': 'core.pagination.CustomPagination',
    'PAGE_SIZE': 20,

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}

SPECTACULAR_SETTINGS = { # Configurações da documentação da API. Responsável pelo Swagger e Redoc
    'TITLE': 'API de Gestão de Eventos',
    'DESCRIPTION': 'API com Auth Token e Filtros Avançados.',
    'VERSION': '1.0.0',
}

JAZZMIN_SETTINGS = { # Configurações do Jazzmin. Responsável pela customização do admin
    "site_title": "Gestão de Eventos",
    "site_header": "Admin Eventos",
    "welcome_sign": "Bem-vindo ao Sistema",
    "search_model": "core.Participante",
}

CORS_ALLOWED_ORIGINS = config('CORS_ORIGINS', default='http://localhost:3000', cast=Csv()) # Configuração CORS via variável de ambiente

CACHES = { # Configuração de cache simples. Pode ser ajustada conforme necessidade.
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
 
LOGGING = { # Configuração básica de logging para registrar eventos importantes
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}