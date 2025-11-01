from django.urls import path
from . import views

app_name = "reports"
urlpatterns = [
    path("", views.ReportsIndexView.as_view(), name="index"),
    path("pdf/<str:time_range>/", views.generate_pdf, name="generate_pdf"),
    path("csv/<str:time_range>/", views.generate_csv, name="generate_csv"),
]