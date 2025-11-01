import datetime
from time import timezone
from django.contrib import admin

from .models import GCalendarReminder, GCalendarSyncSettings, GCalendarEvent


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

    def sync_now(self, request, queryset):
        synced = 0
        for item in queryset:
            if item.enabled:
                # Here you would add the logic to trigger synchronization
                item.last_synced = datetime.datetime.now(datetime.timezone.utc)
                item.save()
                synced += 1
        self.message_user(request, f'{synced} calendar(s) synchronization triggered. {item.calendar_id}')
    sync_now.short_description = "Sync selected calendars now"
    

@admin.register(GCalendarEvent)
class GCalendarEventAdmin(admin.ModelAdmin):
    list_display = ("summary", "event_id", "start_time", "end_time", "sync_settings", "booking",)
    search_fields = ("summary", "event_id",)
    list_filter = ("sync_settings",)
    ordering = ("-start_time",)
    readonly_fields = ("created_at", "updated_at",)
    