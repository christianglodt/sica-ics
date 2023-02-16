# sica-ics.py
Python CGI script to generate an ics file with calendar data scraped from the SICA website.

## Configuration
The environment variable COMMUNE_ID should be set to the identifier of the commune from the SICA website.

To find the identifier, visit https://sicaapp.lu/commune/, select a commune and click Save. Then reload the main page at https://sicaapp.lu, and inspect the cookies set by the page in your browser. The cookie named "commune_id" will have the value for the selected commune.

The START_HOUR and END_HOUR environment variables can be set to the desired start and end hour of the generated events. Defaults are 6 and 10 respectively.
