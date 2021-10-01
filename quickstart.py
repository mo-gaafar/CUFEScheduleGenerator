from __future__ import print_function
import datetime
import sys
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from posixpath import split
import htmlparser
import datetime
import pytz
from tzlocal import get_localzone

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def weekdaytonum(weekday):
    if weekday == 'Monday':
        return 0
    elif weekday == 'Tuesday':
        return 1
    elif weekday == 'Wednesday':
        return 2
    elif weekday == 'Thursday':
        return 3
    elif weekday == 'Friday':
        return 4
    elif weekday == 'Saturday':
        return 5
    elif weekday == 'Sunday':
        return 6


"""
Shifts times from 1-7pm to 24H format
"""


def timefix(timestring):
    splittime = timestring.split(':')

    fixedtime = timestring
    # print(timestring)

    if int(splittime[0]) >= 1 and int(splittime[0]) <= 7:
        tempfix = int(splittime[0])+12
        fixedtime = str(str(tempfix) + ':' + splittime[1])
    # print(fixedtime)
    return str(fixedtime)


def main():
    """
    User input main menu
    """

    needhelp = input("Do you want a quick guide on how to use this? (Y/N) ")

    if needhelp == 'Y':
        print("Steps: \n 1.Log into chreg.cu.eng.eg \n 2.Open the My Timetable icon \n 3.ctrl+s to save the website as \n 4.Save it in the same file as the .exe of this program and proceed ")

    filename = input("Enter filename: ")
    newcalname = input("Enter desired calendar name: ")

    startdatetemp = input("Enter startdate (YYYY/MM/DD): ").split('/')
    startdate = datetime.date(int(startdatetemp[0]), int(
        startdatetemp[1]), int(startdatetemp[2]))
    repeatcount = str(input("Repeat for how many weeks? "))

    runbool = input("Confirm and run program? Y/N")
    if runbool != 'Y':
        print("Exiting Program, nothing was done")
        sys.exit()

    # Timezone finder
    local_tz = str(get_localzone())
    print(local_tz)

    """
    Calls the HTML parsing script
    """

    eventarr = htmlparser.parsehtml(filename)

    """
    Event parsing
    """

    class eventobject:

        def __init__(self, event, startdate=datetime.date.today(), repeatcount=12):
            eventchunk = event.split(',')
            self.dayofweek = eventchunk[0]
            self.dayofweeknum = weekdaytonum(self.dayofweek)
            self.code = eventchunk[1]
            self.name = eventchunk[2]
            self.tutorialorlecture = eventchunk[3]
            self.location = eventchunk[4]
            self.capacity = eventchunk[5]
            self.timestart = timefix(eventchunk[6])
            self.timeend = timefix(eventchunk[7])
            # startdate = #datetime.date.today()  # - datetime.timedelta(days=14)
            # pretty reliable stuff XD
            difference = -(startdate.weekday()-self.dayofweeknum)
            self.exactdate = startdate + datetime.timedelta(days=difference)
            self.eventtitle = self.code + ' ' + self.tutorialorlecture + ' ' + self.name
            self.isostart = datetime.datetime.combine(
                self.exactdate, datetime.datetime.strptime(self.timestart, "%H:%M").time()).isoformat()
            self.isoend = datetime.datetime.combine(
                self.exactdate, datetime.datetime.strptime(self.timeend, "%H:%M").time()).isoformat()

            # to be input by the user later
            self.repeatfreq = 'WEEKLY'
            self.repeatcount = repeatcount

    splitarr = []
    caleventarr = []
    for event in eventarr:
        splitarr.append(eventobject(event, startdate, repeatcount))
        # array of dictionaries
    for event in splitarr:
        caleventarr.append({
            'summary': event.eventtitle,
            'location': event.location,
            'description': '',
            'start': {
                'dateTime': event.isostart,
                'timeZone': local_tz,
            },
            'end': {
                'dateTime':   event.isoend,
                'timeZone': local_tz,
            },
            'recurrence': [
                'RRULE:FREQ='+event.repeatfreq+';COUNT='+event.repeatcount
            ],
            # 'attendees': [
            #     {'email': 'lpage@example.com'},
            #     {'email': 'sbrin@example.com'},
            # ],
            'reminders': {
                'useDefault': True,
                # 'overrides': [
                #     {'method': 'email', 'minutes': 24 * 60},
                #     {'method': 'popup', 'minutes': 10},
                # ],
            },
        })

    """
    Google Calendar API .
    """
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

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

    # Calendar creator
    request_body = {
        'summary': newcalname
    }

    response = service.calendars().insert(body=request_body).execute()
    print(response)

    # Event creator

    for event in caleventarr:
        event = service.events().insert(
            calendarId=response['id'], body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    confirmcreation = input(
        "Are you sure you want to keep this calendar? (Y/N) ")

    # deletes calendar if user doesnt want to keep it
    if confirmcreation == 'N':
        service.calendars().delete(calendarId=response['id']).execute()


if __name__ == '__main__':
    main()
