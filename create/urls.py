from django.urls import path
from .views import CreateSongView, MeaningView, SunoGenerateView, SunoCallbackView

urlpatterns = [
    # 곡 메타 정보 생성
    path("song/", CreateSongView.as_view(), name="create-song"),

    # 단어 의미 조회
    path("meaning/<str:word>/", MeaningView.as_view(), name="create-meaning"),

    # Suno AI 를 이용한 곡 생성
    # 최종 URL: /api/create/<song_id>/
    path("<int:song_id>/", SunoGenerateView.as_view(), name="suno-generate"),

    # Suno 콜백 엔드포인트
    # 최종 URL: /api/create/callback/
    path("callback/", SunoCallbackView.as_view(), name="suno-callback"),
]
