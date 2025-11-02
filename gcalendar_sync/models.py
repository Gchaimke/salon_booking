import logging
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from gcalendar_sync.utils import remove_event

try:
    # Import Booking model if available
    from booking.models import Booking
except ImportError:
    Booking = None


logger = logging.getLogger(__name__)


class GCalendarSyncSettings(models.Model):
    """Model to store Google Calendar synchronization settings."""
    enabled = models.BooleanField(
        default=True, help_text="Enable or disable Google Calendar synchronization.")
    calendar_id = models.CharField(
        max_length=255, default='primary', help_text="Google Calendar ID to sync with. ( use 'primary' for main calendar )")
    last_synced = models.DateTimeField(
        null=True, blank=True, help_text="Timestamp of the last synchronization.")

    def __str__(self):
        return f"Calendar Sync Settings ID:{self.calendar_id}"

    class Meta:
        verbose_name = "Calendar Sync Settings"
        verbose_name_plural = "Calendar Sync Settings"


class GCalendarReminder(models.Model):
    """Model to store Google Calendar reminder details."""
    method = models.CharField(
        max_length=50, help_text="Method of the reminder", choices=[('email', 'Email'), ('popup', 'Popup')])
    minutes_before = models.IntegerField(
        help_text="Number of minutes before the event when the reminder should trigger.")
    event = models.ForeignKey(
        'GCalendarSyncSettings', on_delete=models.CASCADE, related_name='reminders',
        help_text="The Google Calendar sync settings this reminder is associated with.")

    def __str__(self):
        return f"Reminder: {self.method} {self.minutes_before} minutes before"

    class Meta:
        verbose_name = "Google Calendar Reminder"
        verbose_name_plural = "Google Calendar Reminders"


class GCalendarEvent(models.Model):
    """Model to store Google Calendar event details."""
    if Booking:
        booking = models.ForeignKey(
            Booking, blank=True, null=True, on_delete=models.CASCADE, related_name='gcalendar_events',
            help_text="The booking this event is associated with.")
    sync_settings = models.ForeignKey(
        'GCalendarSyncSettings', on_delete=models.CASCADE, related_name='events',
        help_text="The Google Calendar sync settings this event is associated with.")
    event_id = models.CharField(
        max_length=255, unique=True, help_text="Unique ID of the Google Calendar event.")
    summary = models.CharField(
        max_length=255, help_text="Summary or title of the event.")
    description = models.TextField(
        blank=True, help_text="Detailed description of the event.")
    start_time = models.DateTimeField(help_text="Start time of the event.")
    end_time = models.DateTimeField(help_text="End time of the event.")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the event was created in the system.")
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the event was last updated in the system.")

    def __str__(self):
        return f"Event: {self.summary} (ID: {self.event_id})"

    class Meta:
        verbose_name = "Google Calendar Event"
        verbose_name_plural = "Google Calendar Events"


@receiver(post_delete, sender=GCalendarEvent)
def remove_event_from_google_calendar(sender, instance, using, **kwargs):
    # Custom logic to be executed on object deletion
    logger.warning(f"Object {instance} of {sender.__name__} was deleted with {using}.")
    sync_settings = GCalendarSyncSettings.objects.filter(enabled=True).last()
    calendar_id = 'primary'
    if sync_settings:
        calendar_id = sync_settings.calendar_id

    logger.warning(f"Also removing event from Google Calendar: {instance.event_id=}.")
    remove_event(instance.event_id, calendar_id=calendar_id)