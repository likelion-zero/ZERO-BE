from django.urls import path
from .views import PlaySongView

urlpatterns = [
    path("play/<int:song_id>/", PlaySongView.as_view(), name="playlist-play"),
]