from django.urls import path
from .views import SongCreateView

urlpatterns = [
    path("create/", SongCreateView.as_view()),
]
