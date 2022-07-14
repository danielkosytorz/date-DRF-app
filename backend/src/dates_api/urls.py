from django.urls import path
from rest_framework.routers import DefaultRouter

from src.dates_api.views import DateViewSet, PopularMonthListView

app_name = "dates_api"

router = DefaultRouter()
router.register("dates", DateViewSet, basename="dates")

urlpatterns = [
    path("popular/", PopularMonthListView.as_view(), name="popular_month"),
]
urlpatterns += router.urls
