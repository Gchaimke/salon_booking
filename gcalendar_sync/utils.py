from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
from pathlib import Path

SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = Path(__file__).resolve().parent.parent.joinpath('gcalendar_sync')
CREDS_PATH = BASE_DIR / 'secrets' / 'credentials.json'
TOKEN_PATH = BASE_DIR / 'secrets' / 'token.json'

def get_calendar_service():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_events():
    service = get_calendar_service()

    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"{start} - {event['summary']}")

if __name__ == '__main__':
    get_events()