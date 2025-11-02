from django.urls import path

from .views import BookingCreateWizardView


urlpatterns = [
    path("", BookingCreateWizardView.as_view(), name="create_booking"),
]
