import os
import datetime
import pickle

from fastapi import FastAPI
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

app = FastAPI()

# Define the scopes required (read-only access in this case)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Filenames for OAuth2 credentials and token storage
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = '/secret/token.pickle'

# Calendar ID for your calendar (set via environment or use default)
CALENDAR_ID = os.getenv('CALENDAR_ID')


def get_credentials():
    """
    Obtains OAuth2 credentials for a user account.
    The credentials are saved in a local token file (TOKEN_FILE) for reuse.
    """
    creds = None
    # Check if token file exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    # If there are no valid credentials, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Run the local server flow to get new credentials
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for future runs
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_today_events(service, calendar_id=CALENDAR_ID):
    """
    Retrieves all events scheduled for the current day from the specified calendar.
    The time window is defined in UTC from 00:00 to 23:59.
    """
    now = datetime.datetime.utcnow()
    start_of_day = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    end_of_day = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
    
    # Convert to ISO 8601 format with 'Z' indicating UTC time.
    time_min = start_of_day.isoformat() + 'Z'
    time_max = end_of_day.isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    return events


def check_shifts(events):
    """
    Filters the retrieved events to identify shift events that are still marked as 'Closed'.
    This example assumes that shift events include the keyword 'Shift'
    and a closed shift is indicated by the word 'Closed' in the event summary.
    """
    closed_shifts = []
    for event in events:
        summary = event.get('summary', '')
        if "Shift" in summary and "Closed" in summary:
            closed_shifts.append(event)
    return closed_shifts


def perform_business_logic(shift):
    """
    Executes business logic for a closed shift.
    In this prototype, it prints a message; replace this with actions such as notifications,
    logging, or triggering other workflows.
    """
    shift_summary = shift.get('summary', 'No Title')
    start_time = shift.get('start', {}).get('dateTime', shift.get('start', {}).get('date'))
    print(f"Shift still closed: '{shift_summary}' at {start_time}. Executing business logic.")


# Global variable for the Google Calendar service client (lazy initialization)
service = None


def get_calendar_service():
    global service
    if service is None:
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
        print("calendar")
    return service


@app.get("/")
async def read_root():
    """
    Simple health-check endpoint.
    """
    return {"message": "Calendar Bot is running."}


@app.get("/events")
async def events():
    """
    Retrieves today's events from the Google Calendar.
    """
    cal_service = get_calendar_service()
    events = get_today_events(cal_service)
    if not events:
        return {"message": "No events found for today."}
    return {"events": events}


@app.get("/check_shifts")
async def check_shifts_endpoint():
    """
    Checks today's events for closed shifts and performs the defined business logic.
    """
    cal_service = get_calendar_service()
    events = get_today_events(cal_service)
    closed_shifts = check_shifts(events)
    if closed_shifts:
        for shift in closed_shifts:
            perform_business_logic(shift)
        return {
            "message": "Business logic executed for closed shifts.",
            "closed_shifts": closed_shifts
        }
    else:
        return {"message": "All shift events are open."}
