from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent



SECRET_KEY = 'django-insecure-&co%ozq83cke8ca0($=s^8-b6%qb9q3r2i2zk4^2j#h*dg_q!j'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'emiliorubio94.pythonanywhere.com']



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'accounts',
    'user_portal',
    'admin_portal',
    'superuser_portal',
    'reservations',
    'social_django',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'admin_portal' / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



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



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'

USE_I18N = True

USE_TZ = True



STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
LOGOUT_REDIRECT_URL = '/accounts/login/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ayanokoji2122@gmail.com'
EMAIL_HOST_PASSWORD = 'qoglzqqzqnjtuuao'

AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '663579820125-gg0547k393709luns7e4e0jdgfcq7mgm.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'https://emiliorubio94.pythonanywhere.com/complete/google-oauth2/'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'accounts.social_auth_pipeline.restrict_email_domain',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'accounts.social_auth_forbidden.forbidden_by_email',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'accounts.social_auth_pipeline.create_profile_if_not_exists',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
)

SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_LOGIN_ERROR_URL = '/accounts/login/?error=forbidden'
SOCIAL_AUTH_BACKEND_ERROR_URL = '/accounts/forbidden/'
SOCIAL_AUTH_AUTHENTICATION_ERROR_URL = '/accounts/forbidden/'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/accounts/login/'
SOCIAL_AUTH_FORBIDDEN_URL = '/accounts/forbidden/'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/user/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'