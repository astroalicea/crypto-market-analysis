from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("chart.png", views.dashboard_chart_view, name="dashboard_chart"),
]
