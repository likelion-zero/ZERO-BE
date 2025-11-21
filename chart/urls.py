from django.urls import path
from .views import ChartView

urlpatterns = [
    path("api/chart/<str:user_id>/", ChartView.as_view(), name="chart-view"),
]