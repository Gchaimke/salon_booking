from django.db import models

class GCalendarSyncSettings(models.Model):
    """Model to store Google Calendar synchronization settings."""
    enabled = models.BooleanField(default=False, help_text="Enable or disable Google Calendar synchronization.")
    calendar_id = models.CharField(max_length=255, blank=True, help_text="Google Calendar ID to sync with.")
    last_synced = models.DateTimeField(null=True, blank=True, help_text="Timestamp of the last synchronization.")

    def __str__(self):
        return f"Google Calendar Sync Settings (Enabled: {self.enabled})"

    class Meta:
        verbose_name = "Google Calendar Sync Settings"
        verbose_name_plural = "Google Calendar Sync Settings"
