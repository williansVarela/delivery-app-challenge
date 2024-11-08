from django.contrib import admin
from django.urls import path

from orders.views import DistanceCalculatorView, HistoryView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DistanceCalculatorView.as_view(), name="home"),
    path("history", HistoryView.as_view(), name="history"),
]
