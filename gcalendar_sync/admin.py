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
    list_display = ("booking", "summary", "start_time",
                    "end_time", "created_at", "updated_at")
    search_fields = ("summary", "event_id", "description")
    list_filter = ("summary",)
    ordering = ("-start_time",)
    readonly_fields = ("created_at", "updated_at",)

    def delete_model(self, request, obj):
        logger.warning(f"About to delete object: {obj}")
        super().delete_model(request, obj)
        logger.warning(f"Object deleted: {obj}")

    def delete_queryset(self, request, queryset):
        logger.warning(f"About to delete queryset: {queryset}")
        super().delete_queryset(request, queryset)
        logger.warning(f"Queryset deleted.")
