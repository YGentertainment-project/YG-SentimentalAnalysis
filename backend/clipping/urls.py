from django.urls.conf import path
from clipping.views import KeywordAPI, ClippingGroupAPI
from django.views.decorators.csrf import csrf_exempt
from clipping.views import (base, preview)

app_name = "clipping"

urlpatterns = [
    path("", base, name="base"),
    path("preview/", preview, name="preview"),
    path("keyword/", csrf_exempt(KeywordAPI.as_view()), name="keyword_api"),
    path("clipgroup/", csrf_exempt(ClippingGroupAPI.as_view()), name="clipping_api")
]
