from posixpath import split
import htmlparser
import datetime
import pytz
from tzlocal import get_localzone


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


eventarr = htmlparser.parsehtml('test2.html')

local_tz = get_localzone()
print(local_tz)


class eventobject:

    def __init__(self, event):
        eventchunk = event.split(',')
        self.dayofweek = eventchunk[0]
        self.dayofweeknum = weekdaytonum(self.dayofweek)
        self.code = eventchunk[1]
        self.name = eventchunk[2]
        self.tutorialorlecture = eventchunk[3]
        self.location = eventchunk[4]
        self.capacity = eventchunk[5]
        self.timestart = eventchunk[6]
        self.timeend = eventchunk[7]
        now = datetime.date.today()  # - datetime.timedelta(days=14)
        # pretty reliable stuff XD
        difference = -(now.weekday()-self.dayofweeknum)
        self.exactdate = now + datetime.timedelta(days=difference)
        self.eventtitle = self.code + ' ' + self.tutorialorlecture + ' ' + self.name
        self.isostart = datetime.datetime.combine(
            self.exactdate, datetime.datetime.strptime(self.timestart, "%H:%M").time()).isoformat()
        self.isoend = datetime.datetime.combine(
            self.exactdate, datetime.datetime.strptime(self.timeend, "%H:%M").time()).isoformat()
        # to be input by the user
        self.repeatfreq = 'WEEKLY'
        self.repeatcount = '14'


splitarr = []
caleventarr = []
for event in eventarr:
    splitarr.append(eventobject(event))
    # array of dictionaries
for event in splitarr:
    caleventarr.append({
        'summary': event.eventtitle,
        'location': event.location,
        'description': '',
        'start': {
            'dateTime': event.isostart + '-00:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime':   event.isoend + '-00:00',
            'timeZone': 'America/Los_Angeles',
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


