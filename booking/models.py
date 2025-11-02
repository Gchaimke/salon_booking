from django.conf import settings
from django.db import models

BOOKING_PERIOD = (
    ("0", "0M"),
    ("5", "5M"),
    ("10", "10M"),
    ("15", "15M"),
    ("20", "20M"),
    ("25", "25M"),
    ("30", "30M"),
    ("35", "35M"),
    ("40", "40M"),
    ("45", "45M"),
    ("60", "1H"),
    ("75", "1H 15M"),
    ("90", "1H 30M"),
    ("105", "1H 45M"),
    ("120", "2H"),
    ("150", "2H 30M"),
    ("180", "3H"),
)


class BookingSettings(models.Model):
    # General
    booking_enable = models.BooleanField(default=True)
    confirmation_required = models.BooleanField(default=True)
    # Date
    disable_weekend = models.BooleanField(default=True)
    available_booking_months = models.IntegerField(
        default=1, help_text="if 2, user can only book booking for next two months.")
    # Time
    start_time = models.TimeField(help_text='Start Time for available booking')
    end_time = models.TimeField(help_text='End Time for available booking')
    pause_between_bookings = models.CharField(
        max_length=3, default="0", choices=BOOKING_PERIOD, help_text="How long to wait between bookings.")

    class Meta:
        verbose_name = "Booking Settings"
        verbose_name_plural = "Booking Settings"


class BookingService(models.Model):
    booking_settings = models.ForeignKey(
        BookingSettings, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    duration = models.CharField(
        max_length=3, choices=BOOKING_PERIOD, help_text="How long each booking take.")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.name} - {self.duration} minutes - {self.price}'


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, blank=True, null=True)
    service = models.ForeignKey(
        BookingService, on_delete=models.CASCADE, related_name='bookings', blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    user_name = models.CharField(max_length=250)
    user_email = models.EmailField()
    approved = models.BooleanField(default=False)
    user_mobile = models.CharField(blank=True, null=True, max_length=15)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user_name or "(No Name)"
