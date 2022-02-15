from django.urls.conf import path
from clipping.views import KeywordAPI, ClippingGroupAPI
from django.views.decorators.csrf import csrf_exempt

app_name = "clipping"

urlpatterns = [
    path("keyword/", csrf_exempt(KeywordAPI.as_view()), name="keyword_api"),
    path("clipgroup/", csrf_exempt(ClippingGroupAPI.as_view()), name="clipping_api")
]