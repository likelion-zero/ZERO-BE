from django.urls import path
from .views import CreateSongView, MeaningView

urlpatterns = [
    path("song/", CreateSongView.as_view(), name="create-song"),
    path("meaning/<str:word>/", MeaningView.as_view(), name="create-meaning"),
]