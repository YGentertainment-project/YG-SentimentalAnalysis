"""yg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.shortcuts import redirect
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', lambda req: redirect('report/')),
    path('admin/', admin.site.urls),
    path("account/", include("account.urls")),
    path("clipping/", include("clipping.urls")),
    path("config/", include("config.urls")),
    path("crawler/", include("crawler.urls")),
    path("report/", include("report.urls"))
]

