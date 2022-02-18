# from config.views import *
from django.conf import settings
from django.conf.urls import static
from django.urls import re_path
from django.views.generic import TemplateView
from crawler import views


app_name = 'crawler'

urlpatterns = [
    re_path(r"^$", TemplateView.as_view(template_name="crawler.html"), name="home"),
    re_path(r"^api/crawl/", views.crawl, name="crawl"),
    re_path(r"^api/schedule/", views.schedule, name="schedule")
]

if settings.DEBUG:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)