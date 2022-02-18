# coding=utf-8
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_ROUTERS = [
    "yg.dbrouter.Router",
]

DATABASES = {
    "default":{
        "ENGINE": "django.db.backends.mysql",
        "HOST": "yg-mariadb",
        "PORT": 3306,
        "NAME": "ygenter",
        "USER": "ygenter",
        "PASSWORD": "ygenter",
    },
    "mongo":{
        "ENGINE": "djongo",
        # "ENFORCE_SCHEMA": True,
        "NAME": "ygenter",
        "CLIENT": {
            "host": "yg-mongodb",
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

DATA_DIR = f"{BASE_DIR}/data"