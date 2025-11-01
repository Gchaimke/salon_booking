"""
Google Calendar utility functions for authentication and event management.
Handles long-lived tokens for seamless integration.
Manage API credentials in https://console.cloud.google.com.
Calendar API interactions: fetch, add, remove events.
API Docs: https://developers.google.com/workspace/calendar/api/v3/reference

API response example:
{'kind': 'calendar#event',
'etag': '"3524994654"',
'id': '7uq9dk6c',
'status': 'confirmed',
'htmlLink': 'https://www.google.com/calendar/event?eid=N3V2NoYWlta2VAbQ',
'created': '2025-11-01T19:14:27.000Z',
'updated': '2025-11-01T19:14:27.997Z',
'summary': 'Test Event',
'creator': {'email': 'gchaimke@gmail.com', 'self': True},
'organizer': {'email': 'gchaimke@gmail.com', 'self': True},
'start': {'dateTime': '2025-11-01T22:14:28+02:00', 'timeZone': 'UTC'},
'end': {'dateTime': '2025-11-01T23:14:28+02:00', 'timeZone': 'UTC'},
'iCalUID': '7uq9dk6c@google.com',
'sequence': 0,
'reminders': {'useDefault': True},
'eventType': 'default'}

"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent.parent.joinpath('gcalendar_sync')
CREDS_PATH = BASE_DIR / 'secrets' / 'credentials.json'
TOKEN_PATH = BASE_DIR / 'secrets' / 'token.json'


class GoogleCalendarAuth:
    """
    Manages Google Calendar authentication with long-lived tokens.
    """

    def __init__(self, credentials_path=None, token_path=None):
        self.credentials_path = credentials_path or CREDS_PATH
        self.token_path = token_path or TOKEN_PATH
        self.scopes = ['https://www.googleapis.com/auth/calendar']

    def get_credentials(self):
        """
        Get valid credentials, refreshing or re-authenticating as needed.
        """
        creds = self._load_existing_credentials()

        if not self._are_credentials_valid(creds):
            creds = self._refresh_or_reauth(creds)
            self._save_credentials(creds)

        return creds

    def _load_existing_credentials(self):
        """Load credentials from token file."""
        if self.token_path.exists():
            try:
                return Credentials.from_authorized_user_file(
                    self.token_path, self.scopes
                )
            except Exception as e:
                logger.warning(f"Failed to load credentials: {e}")
        return None

    def _are_credentials_valid(self, creds):
        """Check if credentials are valid and not expired."""
        return creds and creds.valid

    def _refresh_or_reauth(self, creds):
        """Refresh existing credentials or perform new authentication."""
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Successfully refreshed credentials")
                return creds
            except Exception as e:
                logger.warning(f"Failed to refresh credentials: {e}")

        # Perform new authentication
        return self._authenticate()

    def _authenticate(self):
        """Perform OAuth2 authentication flow."""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path, self.scopes
        )

        # Important: Use offline access to get refresh token
        creds = flow.run_local_server(
            port=0,
            access_type='offline',  # Gets refresh token
            prompt='consent'        # Forces consent screen to get refresh token
        )

        logger.info("Completed authentication flow")
        return creds

    def _save_credentials(self, creds):
        """Save credentials to token file."""
        try:
            # Ensure directory exists
            self.token_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            logger.info("Saved credentials")
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")


def get_events(calendar_id='primary'):
    auth = GoogleCalendarAuth()
    service = build('calendar', 'v3', credentials=auth.get_credentials())

    now = datetime.datetime.now(
        datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
    logger.info('Getting the upcoming 500 events with Salon Booking System tag')
    events_result = service.events().list(
        calendarId=calendar_id, timeMin=now, maxResults=500, singleEvents=True, orderBy='startTime', q='Salon Booking System').execute()
    events = events_result.get('items', [])

    if not events:
        logger.info('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        logger.info(
            f"{event['id']=} {start} - {end} : {event.get('summary', 'No Title')}")


def add_event(calendar_id='primary', summary='New Event', description=None, start_time=None, end_time=None):
    if start_time is None or end_time is None:
        raise ValueError("start_time and end_time must be provided")

    if isinstance(start_time, datetime.datetime):
        start_time = start_time.isoformat()

    if isinstance(end_time, datetime.datetime):
        end_time = end_time.isoformat()

    try:
        auth = GoogleCalendarAuth()
        service = build('calendar', 'v3', credentials=auth.get_credentials())

        event = {
            'summary': summary,
            'description': f'{description or ""} - Salon Booking System',
            # "source": {
            #     'title': 'Salon Booking System',
            #     'url': 'https://salon-booking-system.com',
            # },
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 2 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        service.events().insert(calendarId=calendar_id, body=event).execute()
        logger.info(f"Event added: {summary}")
        return True
    except Exception as e:
        logger.error(f"Failed to add event: {e}")
        return False


def update_event(event_id, calendar_id='primary', summary=None, description=None, start_time=None, end_time=None):
    if not event_id:
        raise ValueError("event_id must be provided")

    try:
        auth = GoogleCalendarAuth()
        service = build('calendar', 'v3', credentials=auth.get_credentials())

        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

        if summary:
            event['summary'] = summary

        if description:
            event['description'] = f'{description} - Salon Booking System'

        if start_time:
            if isinstance(start_time, datetime.datetime):
                start_time = start_time.isoformat()
            event['start'] = {
                'dateTime': start_time,
                'timeZone': 'UTC',
            }
        if end_time:
            if isinstance(end_time, datetime.datetime):
                end_time = end_time.isoformat()
            event['end'] = {
                'dateTime': end_time,
                'timeZone': 'UTC',
            }

        updated_event = service.events().update(
            calendarId=calendar_id, eventId=event_id, body=event).execute()
        logger.info(
            f"Event updated: {updated_event.get('summary', 'No Title')}")
        return True
    except Exception as e:
        logger.error(f"Failed to update event: {e}")
        return False


def remove_event(event_id, calendar_id='primary'):
    if not event_id:
        raise ValueError("event_id must be provided")

    try:
        auth = GoogleCalendarAuth()
        service = build('calendar', 'v3', credentials=auth.get_credentials())

        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        logger.info(f"Event removed: {event_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to remove event: {e}")
        return False


if __name__ == '__main__':
    # add_event(
    #     summary='Test Event 3',
    #     start_time=datetime.datetime.now(
    #         datetime.timezone.utc) + datetime.timedelta(minutes=10),
    #     end_time=datetime.datetime.now(
    #         datetime.timezone.utc) + datetime.timedelta(hours=2)
    # )
    get_events()
    # remove_event('akdsqtvr5tc90ganttgla3fhuk')
    # update_event(
    #     event_id='akdsqtvr5tc90ganttgla3fhuk',
    #     summary='Updated Test Event 3',
    #     description='This is an updated test event 3.',
    #     start_time='2025-11-01T22:15:23+02:00',
    #     end_time='2025-11-01T22:24:23+02:00'
    # )
    # get_events()
