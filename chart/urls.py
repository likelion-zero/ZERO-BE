from django.urls import path
from .views import ChartView

urlpatterns = [
    path("<str:user_id>/", ChartView.as_view(), name="chart-view"),
]