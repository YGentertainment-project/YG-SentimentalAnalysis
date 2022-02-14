# coding=utf-8
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_ROUTERS = [
    "yg.dbrouter.Router",
]

DATABASES = {
    "default":{
        "ENGINE": "django.db.backends.mysql",
        "HOST": "127.0.0.1",
        "PORT": 1398,
        "NAME": "ygenter",
        "USER": "root",
        "PASSWORD": "ygenter",
    },
    "mongo":{
        "ENGINE": "django",
        # "ENFORCE_SCHEMA": True,
        "NAME": "ygenter",
        "CLIENT": {
            "host": "127.0.0.1",
            "port": 1399,
            "username": "ygenter",
            "password": "ygenter",
            "authSource": "admin",
            "authMechanism": "SCRAM-SHA-1"
        }
    }
}

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATA_DIR = f"{BASE_DIR}/data"
