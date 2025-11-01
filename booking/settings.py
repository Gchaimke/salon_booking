from django.conf import settings

BOOKING_PAGINATION = getattr(settings, 'BOOKING_PAGINATION', 50)

BOOKING_SUCCESS_REDIRECT_URL = getattr(settings, 'BOOKING_SUCCESS_REDIRECT_URL', None)

BOOKING_DISABLE_URL = getattr(settings, 'BOOKING_DISABLE_URL', "/")

BOOKING_BG = getattr(settings, 'BOOKING_BG', "img/booking_bg.jpg")

BOOKING_TITLE = getattr(settings, 'BOOKING_TITLE', "Booking")

BOOKING_DESC = getattr(settings, 'BOOKING_DESC', "Make your booking easy and fast with us.")
