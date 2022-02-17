from django.urls import path
from report import views

app_name = "report"

urlpatterns = [
    path("", views.base, name="report"),
    path("preview/", views.preview, name="preview"),
    path('load_data/', views.load_data, name='load_data'),
    path('load_preview/', views.load_preview, name='load_preview'),
]
