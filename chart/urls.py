from django.urls import path
from .views import ChartView

urlpatterns = [
    path("chart/<str:username>", ChartView.as_view()),
]
