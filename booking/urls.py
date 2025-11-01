from django.urls import path
from django.http import JsonResponse
from datetime import datetime

from .views import (BookingHomeView, BookingCreateWizardView, BookingListView,
                    BookingSettingsView, bookingUpdateView, get_available_time)


def get_available_time_view(request):
    date_str = request.GET.get("date")
    if not date_str:
        return JsonResponse({"error": "missing date parameter"}, status=400)
    try:
        date_obj = datetime.fromisoformat(date_str).date()
    except ValueError:
        return JsonResponse({"error": "invalid date format, expected YYYY-MM-DD"}, status=400)
    result = get_available_time(date_obj)
    return JsonResponse(result, safe=False)


urlpatterns = [
    path("", BookingCreateWizardView.as_view(), name="create_booking"),
    path("admin", BookingHomeView.as_view(), name="admin_dashboard"),
    path("admin/list", BookingListView.as_view(), name="booking_list"),
    path("admin/settings", BookingSettingsView.as_view(), name="booking_settings"),
    path("<int:id>/<str:type>", bookingUpdateView, name="booking_update"),
    path("get-available-time", get_available_time_view, name="get_available_time"),
]
