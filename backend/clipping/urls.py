from django.urls import path
from clipping.views import (base)

app_name = 'clipping'

urlpatterns = [
    path("", base, name="clipping"),
]
