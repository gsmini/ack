import datetime
import os
import sys
import environs

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(BASE_DIR, "apps/"))
sys.path.insert(0, os.path.join(BASE_DIR, "utils/"))

env = environs.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))
SECRET_KEY = env.str("SECRET_KEY")

DEBUG = env.bool("DEBUG")
KUBE_CONFIG = os.path.join(BASE_DIR, ".kube.config")
# 用.evn方式来读取配置文件,把.env放在.gitignore中,线上的.env中的配置是正式环境相关配置．
ALLOWED_HOSTS_STR = env.str("ALLOWED_HOSTS")
if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = ALLOWED_HOSTS_STR.split(",")

SECRET_KEY = "6okdaz$3=1w_4i!-r!#6wh-e!8%3v75a4j+^xm09s2&4#)40#i"

# SECURITY WARNING: don't run with debug turned on in production!

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.audit",
    "apps.clusterrole",
    "apps.clusterrolebinding",
    "apps.configmap",
    "apps.cronjob",
    "apps.daemonset",
    "apps.deployment",
    "apps.event",
    "apps.ingress",
    "apps.job",
    "apps.namespace",
    "apps.node",
    "apps.pod",
    "apps.pv",
    "apps.pvc",
    "apps.rolebinding",
    "apps.secret",
    "apps.service",
    "apps.serviceaccount",
    "apps.statefulset",
    "apps.storageclass",
    "apps.user",  # 用户管理以及文件方式部署yaml
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ack.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ack.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/
# DRF
REST_FRAMEWORK = {
    # 　认证方式
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    # 权限
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

if not DEBUG:
    # 正式环境的时候需配置返回为jons渲染器，不然会暴露drf样式 html给用户
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
        "rest_framework.renderers.JSONRenderer"
    ]

# JWT_AUTH ：声明JWT_AUTH相关全局配置
# jwt-token的过期时间设置,days=7表示获取一次jwt token可以用7天
JWT_AUTH = {
    "JWT_EXPIRATION_DELTA": datetime.timedelta(days=30),
    # 自定义header = {'Authenticate':'token jwt-token'}中的这个JWT参数，这里我没改
    "JWT_AUTH_HEADER_PREFIX": "token",
}

# 跨域增加忽略
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "POST",
    "PUT",
)

CORS_ALLOW_HEADERS = (
    "Access-Control-Allow-Origin",
    "XMLHttpRequest",
    "X_FILENAME",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "Pragma",
)

# 语言https://www.jb51.net/article/166044.htm
LANGUAGE_CODE = "zh-Hans"
TIME_ZONE = "Asia/Shanghai"  # 上海时区
USE_I18N = True
USE_L10N = True
USE_TZ = False
# 静态文件
if DEBUG:
    STATICFILE_DIRS = [os.path.join(BASE_DIR, "static")]
else:
    STATIC_ROOT = "staticfiles"

STATIC_URL = "/static/"
# k8s客户端请求超时时间
K8S_TIMEOUT = env.int("K8S_TIMEOUT", 3)
# 阿里云oss配置
# 阿里云OSS配置信息
PREFIX = env.str("PREFIX")
END_POINT = env.str("END_POINT")  # OSS存储节点
BUCKET_NAME = env.str("BUCKET_NAME")
MEDIA_URL_ALIYUN = "https://" + BUCKET_NAME + "." + END_POINT + "/"
# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。
ACCESS_KEY_ID = env.str("ACCESS_KEY_ID")
ACCESS_KEY_SECRET = env.str("ACCESS_KEY_SECRET")
