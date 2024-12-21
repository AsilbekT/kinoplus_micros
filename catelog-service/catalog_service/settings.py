from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent



SECRET_KEY = 'django-insecure-c$r8uxk(=f#g(^*ghlct$pp=q+h@67*dq@b49gykl4j66klqf1'
SECRET_KEY_JWT = 'VpwI_yUDuQuhA1VEB0c0f9qki8JtLeFWh3lA5kKvyGnHxKrZ-M59cA'
DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    'https://gateway.pandatv.uz',
    'https://panda-production.netlify.app',
    'https://pandatv.uz',
    "https://admin-panda.vercel.app",
]

SERVICES = {
    "userservice": "https://gateway.pandatv.uz/userservice",
    "authservice": "https://gateway.pandatv.uz",
    "catalogservice": "https://gateway.pandatv.uz/catalogservice",
    "playbackservice": "https://gateway.pandatv.uz/playbackservice",
    "billingservice": "https://gateway.pandatv.uz/billingservice",
    "analiticservice": "https://gateway.pandatv.uz/analitics",
    "videoconversion": "https://gateway.pandatv.uz/videoconversion"
}

CORS_ALLOWED_ORIGINS = [
    "https://gateway.pandatv.uz",
    "http://localhost:8080",
    "http://localhost:5173",
    "https://admin-panda.vercel.app",
    "http://localhost:3000",
    "http://localhost:3001",
    "https://panda-production.netlify.app",
    'https://panda-dashboard-tau.vercel.app',
    'https://pandatv.uz'
]

CORS_ORIGIN_WHITELIST = [
    "https://gateway.pandatv.uz",
    "https://admin-panda.vercel.app",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:3001",
    "https://panda-production.netlify.app",
    'https://panda-dashboard-tau.vercel.app',
    'https://pandatv.uz'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'video_app',
    'video_api',
    'corsheaders',
    'video_search',
    'catalog_management_app',
    'megogo'
]


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
CORS_ALLOW_ALL_ORIGINS = True


ROOT_URLCONF = 'catalog_service.urls'

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

WSGI_APPLICATION = 'catalog_service.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite.db', 
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/catalogservice/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/catalogservice/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
