from django.urls import path
from .views import ChartView

urlpatterns = [
    path('chart/<str:user_id>/', ChartView.as_view()),
]