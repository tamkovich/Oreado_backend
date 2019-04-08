from oreado_backend.settings.base import *
from private import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": DB_CONFIG["name"],
        "USER": DB_CONFIG["user"],
        "PASSWORD": DB_CONFIG["password"],
        "HOST": DB_CONFIG["host"],
        "PORT": DB_CONFIG['port'],
    }
}
