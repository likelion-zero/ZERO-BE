from django.urls import path
from .views import PlaySongView, UserPlaylistView

urlpatterns = [
    path("play/<int:song_id>/", PlaySongView.as_view(), name="playlist-play"),
    path("<str:user_id>/", UserPlaylistView.as_view(), name="playlist-user"),
]