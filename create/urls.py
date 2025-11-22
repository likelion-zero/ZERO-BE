from django.urls import path
from .views import CreateSongView, MeaningView, SunoGenerateView

urlpatterns = [
    path("song/", CreateSongView.as_view(), name="create-song"),
    path("meaning/<str:word>/", MeaningView.as_view(), name="create-meaning"),

    # Suno AI 를 이용한 곡 생성
    # 최종 URL: /api/create/<song_id>/
    path("<int:song_id>/", SunoGenerateView.as_view(), name="suno-generate"),
]