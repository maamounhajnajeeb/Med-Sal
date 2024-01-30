import os
import dj_database_url
from pathlib import Path
from datetime import timedelta
from django.utils.translation import gettext_lazy as _


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "3d9a9c547b8eac4412eae62daa2f250ef81cd94312964e5bf80007cf30014e4c"
# DEBUG = bool(int(os.environ.get("DEBUG", 0)))
DEBUG = True

# ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
ALLOWED_HOSTS = ["medsal-production.up.railway.app", "127.0.0.1"]
ALLOWED_HOSTS.append(
        os.environ.get("Railway_Host", "").split(",")
    )


INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.gis',
    
    # third party packages
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework_simplejwt',
    "rest_framework_gis",
    "rest_framework",
    "corsheaders",
    
    # local apps
    "service_providers.apps.ServiceProvidersConfig",
    "appointments.apps.AppointmentsConfig",
    "notification.apps.NotificationConfig",
    "permissions.apps.PermissionsConfig",
    "deliveries.apps.DeliveriesConfig",
    "contact_us.apps.ContactUsConfig",
    "category.apps.CategoryConfig",
    "services.apps.ServicesConfig",
    "products.apps.ProductsConfig",
    "orders.apps.OrdersConfig",
    "users.apps.UsersConfig",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.language_middleware.language',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
        , ]
    
    , 'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication'
        , )
    
    , 'DEFAULT_THROTTLE_RATES': {
        'un_authenticated': '1/hour'
        , 'authenticated': '2/hour'
        , }
    
    }


SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=20),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=30),
    "ROTATE_REFRESH_TOKENS": True,
    "UPDATE_LAST_LOGIN": False,
    "JTI_CLAIM": "jti" # added by default (for explaination)
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'maamoun.haj.najeeb@gmail.com'
EMAIL_HOST_PASSWORD = 'jrkuwnnkzqqgkkim'
EMAIL_PORT = 587


CORS_ALLOWED_ORIGINS = (
        "http://localhost:3000",
        "http://localhost:8000",
        "https://medsal-production.up.railway.app",
    )

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "https://medsal-production.up.railway.app"
    ]

ROOT_URLCONF = 'core.urls'


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


WSGI_APPLICATION = 'core.wsgi.application'


# Docker
# DATABASES = {
#     "default": dj_database_url.config(
#         default=os.environ.get("DataBase_URL")
#         , conn_max_age=600
#     )
# }
# DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

# Maamoun
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "med_sal", # my database name, you can change
        "USER": "postgres", # your chosen or default database system name
        "PASSWORD": "17AiGz48rhe", #
        "HOST": "", # localhost
        "PORT": "", # 5432
    }
}

# Tareq
# DATABASES = {
#     "default": {
#         "ENGINE": "django.contrib.gis.db.backends.postgis",
#         "NAME": "med_sal", # my database name, you can change
#         "USER": "postgres", # your chosen or default database system name
#         "PASSWORD": get_env_details(), #
#         "HOST": "", # localhost
#         "PORT": "", # 5432
#     }
# }


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


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "static" # for production
STATICFILES_DIRS = [BASE_DIR / "core/assets"] # for development


MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "users.Users"


GDAL_LIBRARY_PATH = 'C:\OSGeo4W\\bin\gdal307.dll'


USE_TZ = True

TIME_ZONE = 'Asia/Riyadh'

LANGUAGE_CODE = "en-us" # default language

LANGUAGES = (
    ("ar", _("Arabic"))
    , ('en', _("English"))
)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000 * 2 # 2 year
# SECURE_SSL_REDIRECT = True

SECURE_REFERRER_POLICY = "strict-origin"

# To support old browsers
SECURE_BROWSER_XSS_FILTER = True

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }
}

AUTHENTICATION_BACKENDS = [
    'users.backend.CustomAuthBackend',
    "django.contrib.auth.backends.ModelBackend"
]
