#!/usr/bin/env python

import requests
import os
import re
import json
import datetime
import icalendar


COMMUNE_ID = os.environ.get('COMMUNE_ID', '24')


def get_pickups():
    response = requests.get('https://sicaapp.lu', cookies={'commune_id': COMMUNE_ID})
    html = response.text

    escaped_json_match = re.search(r'obj = JSON.parse\("(.*)"\);', html)
    if not escaped_json_match:
        raise Exception('Calendar data not found in HTML')

    escaped_json = escaped_json_match.group(1)
    data = json.loads(escaped_json.replace('\\"', '"'))

    for o in data:
        schedule = o['schedule']
        for entry in schedule:
            if entry['pickupTypes']:
                date = datetime.datetime.strptime(entry['date'], '%Y%m%d').date()
                pickups = [pt['name'] for pt in entry['pickupTypes']]
                yield date, pickups


def get_ical():
    cal = icalendar.Calendar()
    cal.add('prodid', 'sica-ics.py')
    cal.add('version', '2.0')

    for date, pickups in get_pickups():
        for pickup in pickups:
            event = icalendar.Event()
            event.add('summary', pickup)
            event.add('dtstart', date)
            event.add('dtend', date + datetime.timedelta(days=1))
            cal.add_component(event)
    
    return cal.to_ical().decode('utf-8')


def main():
    print('HTTP/1.1 200 OK')
    print('Cache-Control: no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
    print('Content-Type: text/calendar')
    print('Pragma: no-cache')
    print('Expires: -1')
    print('Access-Control-Allow-Origin: *')
    print('')
    print(get_ical())


if __name__ == '__main__':
    main()
