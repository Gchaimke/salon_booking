import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View

from booking.models import Booking, BookingAlertEmail

logger = logging.getLogger(__name__)


class BookingSettingMixin(View):
    """
    View mixin which requires that the authenticated user is a staff member
    (i.e. `is_staff` is True).
    """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(settings.LOGIN_URL)
        return super().dispatch(request, *args, **kwargs)


def send_booking_email(booking: Booking):
    from django.template import Template, Context
    from django.core.mail import EmailMultiAlternatives

    default_email_body_template = """Dear {{booking.user_name}},\n\nYour booking for {{booking.service.name}} on 
    {{booking.date}} at {{booking.time}} has been {{booking.approved|yesno:"approved,rejected"}}.\n\nThank you!"""

    email_body = booking.email_alerts.email_body if booking.email_alerts else None
    email_body_template = Template(email_body or default_email_body_template)

    body = email_body_template.render(Context( {'booking': booking}))

    from_email = settings.DEFAULT_FROM_EMAIL or 'webmaster@localhost'
    msg = EmailMultiAlternatives(
        booking.user_email,
        body,
        from_email,
        [booking.user_email],
    )
    logger.info(f'Sending booking email to {booking.user_email} with {body=}')
    # msg.send()
