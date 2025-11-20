# playlist/urls.py
from django.urls import path
from .views import PlaylistListView, PlaylistDeleteView, SongPlayView

urlpatterns = [
    path('playlist/<str:user_id>/', PlaylistListView.as_view()),
    path('playlist/<str:user_id>/del/<int:song_id>/', PlaylistDeleteView.as_view()),
    path('playlist/play/<int:song_id>/', SongPlayView.as_view()),
]
