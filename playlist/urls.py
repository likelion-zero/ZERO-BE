from django.urls import path
from .views import PlaySongView, UserPlaylistView, DeleteFromPlaylistView

urlpatterns = [
    path("play/<int:song_id>/", PlaySongView.as_view(), name="playlist-play"),
    path("<str:user_id>/", UserPlaylistView.as_view(), name="playlist-user"),
    path("<str:user_id>/del/<int:song_id>/", DeleteFromPlaylistView.as_view()),
]