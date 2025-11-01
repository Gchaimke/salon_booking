from django.contrib import admin

from .models import GCalendarSyncSettings


@admin.register(GCalendarSyncSettings)
class GCalendarSyncSettingsAdmin(admin.ModelAdmin):
    list_display = ("calendar_id", "last_synced", "enabled",)
    list_editable = ("enabled",)
    readonly_fields = ("last_synced",)
    list_filter = ("enabled", )

    actions = ['sync_now']

    def sync_now(self, request, queryset):
        synced = 0
        for item in queryset:
            if item.enabled:
                # Here you would add the logic to trigger synchronization
                synced += 1
        self.message_user(request, f'{synced} calendar(s) synchronization triggered. {item.calendar_id}')
    sync_now.short_description = "Sync selected calendars now"
    
