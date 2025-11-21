from django.urls import path
from .views import SongCreateView, WordMeaningView, SongGenerateView

urlpatterns = [
    path("create", SongCreateView.as_view()),                       # POST /api/create
    path("create/meaning/<str:word>", WordMeaningView.as_view()),  # GET  /api/create/meaning/{word}
    path("create/<int:song_id>", SongGenerateView.as_view()),      # POST /api/create/{song_id}
]
