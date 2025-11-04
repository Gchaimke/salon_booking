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

DEFAULT_EMAIL_BODY = """Dear {{booking.user_name}},\n\nYour booking for {{booking.service.name}} on 
                        {{booking.date}} at {{booking.time}} has been approved.\n\nThank you!"""


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

    def __str__(self) -> str:
        return f"Booking Settings: {self.pk or 'New'}"

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


class BookingAlertEmail(models.Model):
    booking_settings = models.ForeignKey(
        BookingSettings, on_delete=models.CASCADE, related_name='alert_emails', null=True)
    email_subject = models.CharField(
        max_length=250, null=True, blank=True, help_text="Email subject for booking alerts.")
    email_header = models.CharField(
        max_length=250, null=True, blank=True, help_text="Email header for booking alerts.")
    email_body = models.TextField(
        null=True, blank=True, help_text="Email template for booking alerts.", default=DEFAULT_EMAIL_BODY)

    def __str__(self) -> str:
        return f"Booking Alert Email: {self.pk or 'New'}"


class BookingAlertSMS(models.Model):
    booking_settings = models.ForeignKey(
        BookingSettings, on_delete=models.CASCADE, related_name='alert_sms', null=True)
    sms_body = models.TextField(
        null=True, blank=True, help_text="SMS template for booking alerts.")

    def __str__(self) -> str:
        return f"Booking Alert SMS: {self.pk or 'New'}"


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, blank=True, null=True)
    service = models.ForeignKey(
        BookingService, on_delete=models.CASCADE, related_name='bookings', blank=True, null=True)
    email_alerts = models.ForeignKey(
        BookingAlertEmail, blank=True, null=True, related_name='bookings', name='email_alerts', on_delete=models.SET_NULL, default=BookingAlertEmail.objects.first)
    sms_alerts = models.ForeignKey(
        BookingAlertSMS, blank=True, null=True, related_name='bookings', name='sms_alerts', on_delete=models.SET_NULL, default=BookingAlertSMS.objects.first)
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

    def save(self, *args, **kwargs):
        if self.pk:  # Check if the object already exists (i.e., it's an update)
            original = Booking.objects.get(pk=self.pk)
            if original.approved != self.approved:
                from booking.utils import send_booking_email
                send_booking_email(self)
        super().save(*args, **kwargs)
