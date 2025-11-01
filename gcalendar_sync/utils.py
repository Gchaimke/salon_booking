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


def get_events():
    auth = GoogleCalendarAuth()
    service = build('calendar', 'v3', credentials=auth.get_credentials())

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