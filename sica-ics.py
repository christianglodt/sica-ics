#!/usr/bin/env python

import requests
import os
import re
import json
import datetime
import icalendar


COMMUNE_ID = os.environ.get('COMMUNE_ID', '24')
EVENT_START_HOUR = int(os.environ.get('START_HOUR', '6'))
EVENT_START_MINUTE = int(os.environ.get('START_MINUTE', '0'))
EVENT_END_HOUR = int(os.environ.get('END_HOUR', '10'))
EVENT_END_MINUTE = int(os.environ.get('END_MINUTE', '0'))


def get_pickups():
    response = requests.get('https://sicaapp.lu', cookies={'commune_id': COMMUNE_ID})
    html = response.text

    escaped_json_match = re.search(r'obj = JSON.parse\("(.*)"\);', html)
    if not escaped_json_match:
        raise Exception('Calendar data not found in HTML')

    escaped_json = escaped_json_match.group(1)
    json_txt = escaped_json.replace('\\"', '"')
    while json_txt.startswith('\\r') or json_txt.startswith('\\n'):
        json_txt = json_txt[2:]
    data = json.loads(json_txt)

    for o in data:
        schedule = o['schedule']
        for entry in schedule:
            if entry['pickupTypes']:
                dt = datetime.datetime.strptime(entry['date'], '%Y%m%d')
                pickups = [pt['name'] for pt in entry['pickupTypes']]
                yield dt, pickups


def get_ical():
    cal = icalendar.Calendar()
    cal.add('prodid', 'sica-ics.py')
    cal.add('version', '2.0')

    for dt, pickups in get_pickups():
        for pickup in pickups:
            event = icalendar.Event()
            event.add('summary', pickup)
            event.add('dtstart', dt + datetime.timedelta(hours=EVENT_START_HOUR, minutes=EVENT_START_MINUTE))
            event.add('dtend', dt + datetime.timedelta(hours=EVENT_END_HOUR, minutes=EVENT_END_MINUTE))
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
