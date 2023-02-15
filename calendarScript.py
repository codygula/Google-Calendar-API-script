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

# WORKING thing to add new events to Google calendar.  
# 
# Follow instruction here https://developers.google.com/calendar/api/quickstart/python to create a credentials.json file. This will not work without it.
#
# This is intended to add the times for the Golden hour to Google calendar for each day. Two sets (beginning and end times) per day.
#
# Install Google api thing: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
#
# If this causes errors, delete the token.json file
#
# No considerations taken for DST


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

YEAR = 2023

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

###
### Sunrise
###
def sunrise(month, day):

  newSunrise = {
    'summary': 'Morning Golden Hour',
    'location': 'Seattle, WA',
    'start': {
      'dateTime': sunriseStart(month,day,YEAR),
      'timeZone': 'America/Los_Angeles',
    },
    'end': {
      'dateTime': sunriseEnd(month,day,YEAR),
      'timeZone': 'America/Los_Angeles',
    },
    'recurrence': [
      'RRULE:FREQ=DAILY;COUNT=1'
    ],
    'reminders': {
      'useDefault': False,
      'overrides': [
        {'method': 'popup', 'minutes': 10},
      ],
    },
  }
  return newSunrise

###
### Sunset
###
def sunset(month, day):

  newSunset = {
    'summary': 'Evening Golden Hour',
    'location': 'Seattle, WA',
    'start': {
      'dateTime': sunsetStart(month,day,YEAR),
      'timeZone': 'America/Los_Angeles',
    },
    'end': {
      'dateTime': sunsetEnd(month,day,YEAR),
      'timeZone': 'America/Los_Angeles',
    },
    'recurrence': [
      'RRULE:FREQ=DAILY;COUNT=1'
    ],
    'reminders': {
      'useDefault': False,
      'overrides': [
        {'method': 'popup', 'minutes': 10},
      ],
    },
  }
  return newSunset


def main():
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

        j = 1
        while j <= 12:
          # API call
          i = 1
          while i <= 31:
            try:
              event = service.events().insert(calendarId='cgula7@gmail.com', body=sunrise(j,i)).execute()
              print( 'Event created: %s' % (event.get('htmlLink')))

              event = service.events().insert(calendarId='cgula7@gmail.com', body=sunset(j,i)).execute()
              print( 'Event created: %s' % (event.get('htmlLink')))
              
            except:
              print("Error! Day = ", i, ", Month = ", j)
          i += 1
        j += 1

    except HttpError as error:
        print('An error occurred: %s' % error)

if __name__ == '__main__':
    main()

