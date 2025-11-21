from django.urls import path
from .views import PlaylistListView, PlaylistDeleteView, SongPlayView

urlpatterns = [
    path("playlist/<str:username>", PlaylistListView.as_view()),
    path("playlist/<str:username>/del/<int:song_id>", PlaylistDeleteView.as_view()),
    path("playlist/play/<int:song_id>", SongPlayView.as_view()),
]
