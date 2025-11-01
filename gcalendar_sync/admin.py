from django.contrib import admin

from .models import GCalendarSyncSettings


@admin.register(GCalendarSyncSettings)
class GCalendarSyncSettingsAdmin(admin.ModelAdmin):
    list_display = ("calendar_id", "last_synced", "enabled",)
    list_editable = ("enabled",)
    readonly_fields = ("last_synced",)
    list_filter = ("enabled", )
    
