from django.urls import path

from .views import BookingCreateWizardView


app_name = "booking"
urlpatterns = [
    path("", BookingCreateWizardView.as_view(), name="create_booking"),
]
