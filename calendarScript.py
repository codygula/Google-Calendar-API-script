from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from astral import LocationInfo
from astral.sun import golden_hour
from astral import SunDirection

# (somewhat) WORKING thing to add new events to Google calendar. 
# 
# Follow instruction here https://developers.google.com/calendar/api/quickstart/python to create a credentials.json file. This will not work without it.
#
# This is intended to add the times for the Golden hour to Google calendar for each day. Two sets (beginning and end times) per day.
#
# Install Google api thing: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
#
# ! If this causes errors, delete the token.json file
#
# No considerations taken for DST
#


city = LocationInfo("Seattle", "Washington", "America/Los_Angeles", 47.6062, -122.3321 )

def sunriseStart(mnth, dy, yr):
    time1, time2 = golden_hour(city.observer, direction=SunDirection.RISING, tzinfo=("America/Los_Angeles"), date=datetime.date(yr, mnth, dy))
    return (time1.strftime("%Y-%m-%d") + "T" + time1.strftime("%H:%M:%S") + "-08:00")

def sunriseEnd(mnth, dy, yr):
    time1, time2 = golden_hour(city.observer, direction=SunDirection.RISING, tzinfo=("America/Los_Angeles"), date=datetime.date(yr, mnth, dy))
    return (time2.strftime("%Y-%m-%d") + "T" + time2.strftime("%H:%M:%S") + "-08:00")


def sunsetStart(mnth, dy, yr):
    time1, time2 = golden_hour(city.observer, direction=SunDirection.SETTING, tzinfo=("America/Los_Angeles"), date=datetime.date(yr, mnth, dy))
    return (time1.strftime("%Y-%m-%d") + "T" + time1.strftime("%H:%M:%S") + "-08:00")

def sunsetEnd(mnth, dy, yr):
    time1, time2 = golden_hour(city.observer, direction=SunDirection.SETTING, tzinfo=("America/Los_Angeles"), date=datetime.date(yr, mnth, dy))
    return (time2.strftime("%Y-%m-%d") + "T" + time2.strftime("%H:%M:%S") + "-08:00")



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
YEAR = 2023


newSunrise = {
  'summary': 'Morning Golden Hour',
  'location': 'Seattle, WA',
  'start': {
    'dateTime': sunriseStart(2,24,YEAR),
    'timeZone': 'America/Los_Angeles',
  },
  'end': {
    'dateTime': sunriseEnd(2,24,YEAR),
    'timeZone': 'America/Los_Angeles',
  },
  'recurrence': [
    'RRULE:FREQ=DAILY;COUNT=1'
  ],
  'attendees': [
    {'email': 'cgula7@gmail.com'}
  ],
  'reminders': {
    'useDefault': False,
    'overrides': [
      {'method': 'email', 'minutes': 24 * 60},
      {'method': 'popup', 'minutes': 10},
    ],
  },
}


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    # Stolen from Google https://developers.google.com/calendar/api/quickstart/python
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)


        # API call
        event = service.events().insert(calendarId='cgula7@gmail.com', body=newSunrise).execute()
        print( 'Event created: %s' % (event.get('htmlLink')))
        print(event)

    except HttpError as error:
        print('An error occurred: %s' % error)

if __name__ == '__main__':
    main()

