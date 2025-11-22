"""
URL configuration for zero project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path,include


def index(request):
    # 백엔드 도메인으로 직접 접속했을 때 보이는 간단한 안내
    return HttpResponse("WordlyKMU 백엔드 API 서버입니다. /api/... 경로로 요청해 주세요.")

urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path("api/create/", include("create.urls")),
    path("api/playlist/", include("playlist.urls")),
    path("api/chart/", include("chart.urls")),
]
