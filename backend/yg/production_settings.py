
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "ygenter",
        'USER': "ygenter",
        'PASSWORD': "ygenter",
        'HOST': "yg-as-mariadb",
        'PORT': 3306,
    },
    "mongo": {
        "ENGINE": "djongo",
        # "ENFORCE_SCHEMA": True,
        "NAME": "yg-mongodb",
        "CLIENT": {
            "host": "yg-as-mongodb",
            "port": 27017,
            "username": "ygenter",
            "password": "ygenter",
            "authSource": "admin",
            "authMechanism": "SCRAM-SHA-1"
        }
    }
}

DEBUG = False

ALLOWED_HOSTS = ["*"]

DATA_DIR = "/data"
