import logging
from django.contrib import admin
from gcalendar_sync.utils import remove_event

from .models import GCalendarReminder, GCalendarSyncSettings, GCalendarEvent


logger = logging.getLogger(__name__)


class GCalendarReminderInline(admin.TabularInline):
    model = GCalendarReminder
    extra = 1


@admin.register(GCalendarSyncSettings)
class GCalendarSyncSettingsAdmin(admin.ModelAdmin):
    list_display = ("calendar_id", "last_synced", "enabled",)
    list_editable = ("enabled",)
    readonly_fields = ("last_synced",)
    list_filter = ("enabled", )

    actions = ['sync_now']
    inlines = [GCalendarReminderInline]


@admin.register(GCalendarEvent)
class GCalendarEventAdmin(admin.ModelAdmin):
    list_display = ("summary", "event_id", "start_time",
                    "end_time", "sync_settings", "booking",)
    search_fields = ("summary", "event_id",)
    list_filter = ("sync_settings",)
    ordering = ("-start_time",)
    readonly_fields = ("created_at", "updated_at",)

    def delete_model(self, request, obj):
        logger.warning(f"About to delete object: {obj}")
        sync_settings = GCalendarSyncSettings.objects.filter(
            enabled=True).last()
        remove_event(
            obj.event_id, calendar_id=sync_settings.calendar_id if sync_settings else 'primary')
        super().delete_model(request, obj)
        logger.warning(f"Object deleted: {obj}")

    def delete_queryset(self, request, queryset):
        logger.warning(f"About to delete queryset: {queryset}")
        sync_settings = GCalendarSyncSettings.objects.filter(
            enabled=True).last()
        for obj in queryset:
            remove_event(
                obj.event_id, calendar_id=sync_settings.calendar_id if sync_settings else 'primary')
        super().delete_queryset(request, queryset)
        logger.warning(f"Queryset deleted.")
