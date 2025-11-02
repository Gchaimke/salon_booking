import datetime
import logging
from math import e
from django.urls import path, reverse
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponseRedirect
from booking.models import Booking, BookingSettings, BookingService
from gcalendar_sync.models import GCalendarSyncSettings

logger = logging.getLogger(__name__)


try:
    from gcalendar_sync.models import GCalendarEvent
    from gcalendar_sync.utils import add_event  # type: ignore
    from gcalendar_sync.utils import sync_bookings_with_events
except ImportError:
    GCalendarEvent = None

    def add_event(**kwargs):
        return False

    def sync_bookings_with_events():
        return


class BookingAdmin(admin.ModelAdmin):
    change_list_template = 'booking/admin/change_list.html'
    list_display = ['user', "user_name",
                    "user_email", "date", "time", "service", "approved"]
    list_filter = ["approved", "date", 'user',
                   'user__groups', 'user__is_staff']
    search_fields = ['user__username',
                     "user_name", "user_email", "user_mobile"]
    list_editable = ["approved"]
    list_per_page = 50
    ordering = ["-date", "-time"]
    actions = ['approve_bookings', 'reject_bookings', 'sync_user_and_customer']
    if GCalendarEvent:
        actions.append('sync_with_calendar')

    def approve_bookings(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(
            request, f'{updated} booking(s) successfully approved.')
    approve_bookings.short_description = "Approve selected bookings"

    def reject_bookings(self, request, queryset):
        updated = queryset.update(approved=False)
        self.message_user(
            request, f'{updated} booking(s) successfully rejected.')
    reject_bookings.short_description = "Reject selected bookings"

    def sync_user_and_customer(self, request, queryset):
        matched_count = 0
        not_matched_count = 0
        for booking in queryset:
            if booking.user is None:
                try:
                    user = User.objects.get(email=booking.user_email)
                    booking.user = user
                    booking.save()
                    if not user.first_name and booking.user_name:
                        name_parts = booking.user_name.split(" ", 1)
                        user.first_name = name_parts[0]
                        if len(name_parts) > 1:
                            user.last_name = name_parts[1]
                        user.save()
                    matched_count += 1
                except User.DoesNotExist:
                    not_matched_count += 1
                    continue
        self.message_user(
            request, f'Successfully set {matched_count} users and failed to match {not_matched_count} bookings.')
    sync_user_and_customer.short_description = "Sync user and customer for selected bookings"

    def sync_with_calendar(self, request, queryset):
        if not GCalendarEvent:
            return
        synced_count = 0
        skipped_count = 0
        reminders_overrides = []
        sync_settings = GCalendarSyncSettings.objects.filter(enabled=True).last()
        if sync_settings and hasattr(sync_settings, 'reminders'):
            reminders_overrides = [{'method': reminder.method, 'minutes': reminder.minutes_before} for reminder in sync_settings.reminders.all()]
        for booking in queryset:
            if booking.approved:
                event = GCalendarEvent.objects.filter(booking=booking).first()
                if not event:
                    booking_settings = BookingSettings.objects.first()
                    if booking_settings:
                        event_end_time = datetime.datetime.combine(
                            booking.date, booking.time) + datetime.timedelta(minutes=float(booking.service.duration))
                    add_event(
                        summary=f'Booking {booking.service.name}, duration {booking.service.duration} minutes is approved',
                        description=f'User Email: {booking.user_email}, User Phone: {booking.user_mobile}, Service: {booking.service.name}, Booking ID: {booking.id}',
                        start_time=datetime.datetime.combine(
                            booking.date, booking.time),
                        end_time=event_end_time,
                        reminders_overrides=reminders_overrides
                        )

                    synced_count += 1
                else:
                    skipped_count += 1
        self.message_user(
            request, f'Successfully synced {synced_count} bookings with Google Calendar and skipped {skipped_count} bookings.')
        sync_bookings_with_events()
    sync_with_calendar.short_description = "Sync selected bookings with Google Calendar"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sync_with_calendar/', self.admin_site.admin_view(
                self.sync_all_with_calendar), name='sync_with_calendar'),
        ]
        return custom_urls + urls

    def sync_all_with_calendar(self, request):
        self.sync_with_calendar(request, Booking.objects.all())
        logger.info(f'Calendar synchronization triggered from admin.')
        return HttpResponseRedirect(reverse('admin:booking_booking_changelist'))


admin.site.register(Booking, BookingAdmin)


class BookingServicesInline(admin.StackedInline):
    model = BookingService
    extra = 1
    verbose_name = 'Booking Service'
    verbose_name_plural = 'Booking Services'
    list_display = ['name', 'duration', 'price']


class BookingSettingsAdmin(admin.ModelAdmin):
    inlines = [BookingServicesInline]


admin.site.register(BookingSettings, BookingSettingsAdmin)


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 3
    list_display = ["user_name", "user_email", "date", "time", "approved"]

# Define a new User admin


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name',
                    'last_name', 'is_staff', 'is_active', 'get_user_groups')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    inlines = [BookingInline]

    def get_user_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_user_groups.short_description = 'Groups'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
