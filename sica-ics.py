#!/usr/bin/env python

import requests
import os
import re
import json
import datetime
import icalendar


COMMUNE_ID = os.environ.get('COMMUNE_ID', '5')
EVENT_START_HOUR = int(os.environ.get('START_HOUR', '6'))
EVENT_START_MINUTE = int(os.environ.get('START_MINUTE', '0'))
EVENT_END_HOUR = int(os.environ.get('END_HOUR', '10'))
EVENT_END_MINUTE = int(os.environ.get('END_MINUTE', '0'))


def get_pickups():
    from_date = (datetime.datetime.now() - datetime.timedelta(days=31)).date().isoformat()
    to_date = (datetime.datetime.now() + datetime.timedelta(days=90)).date().isoformat()
    response = requests.get(f'https://dashboard.sicaapp.lu/api/api/app/pickup-date?filter[community_id]={COMMUNE_ID}&filter[dateRange]={from_date},{to_date}')

    data = response.json()

    for entry in data:
        if entry['isDisabled']:
            continue

        dt = datetime.datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S')
        pickup = [entry['pickup_type']['name']['en']]
        yield dt, pickup


def get_ical():
    cal = icalendar.Calendar()
    cal.add('prodid', 'sica-ics.py')
    cal.add('version', '2.0')

    for dt, pickup in get_pickups():
        event = icalendar.Event()
        event.add('summary', pickup)
        event.add('dtstart', dt.replace(hour=0, minute=0, second=0) + datetime.timedelta(hours=EVENT_START_HOUR, minutes=EVENT_START_MINUTE))
        event.add('dtend', dt.replace(hour=0, minute=0, second=0) + datetime.timedelta(hours=EVENT_END_HOUR, minutes=EVENT_END_MINUTE))
        cal.add_component(event)
    
    return cal.to_ical().decode('utf-8')


def main():
    try:
        content = get_ical()
        content_type = 'text/calendar'
        status = '200 OK'
    except Exception as e:
        content = str(e)
        content_type = 'text/plain'
        status = '500 Error'

    print(f'HTTP/1.1 {status}')
    print(f'Status: {status}')
    print('Cache-Control: no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
    print(f'Content-Type: {content_type}')
    print('Pragma: no-cache')
    print('Expires: -1')
    print('Access-Control-Allow-Origin: *')
    print('')
    print(content)


if __name__ == '__main__':
    main()
