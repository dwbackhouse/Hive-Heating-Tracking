# -*- coding: utf-8 -*-
"""
Spyder Editor
"""
#!/usr/bin

import pickle
import os.path
import time
import datetime
import requests
import json

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# Make sure to install (sudo pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib)

from w1thermsensor import W1ThermSensor
from gpiozero import LightSensor
# Make sure to install (sudo apt-get install python3-w1thermsensor)

import speedtest
#  sudo pip3 install speedtest-cli


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
        
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)


try:
    sensor = W1ThermSensor()
except: sensor = ""    

try:
   ldr=LightSensor(27)
except: ldr = ""   

url = "https://api-prod.bgchprod.info:443/omnia/auth/sessions"
payload = "{\r\n    \"sessions\": [\r\n        {\r\n            \"username\": \"######@#####.com\",\r\n            \"password\": \"#######\",\r\n            \"caller\": \"WEB\"\r\n        }\r\n    ]\r\n}"
headers = {
        'Content-Type': 'application/vnd.alertme.zoo-6.1+json',
        'Accept': 'application/vnd.alertme.zoo-6.1+json',
        'X-Omnia-Client': 'Hive Web Dashboard'
}
response = requests.request("POST", url, headers=headers, data = payload)
response_loads=json.loads(response.text)
id=(response_loads['sessions'][0]['id'])

url2 = "https://api-prod.bgchprod.info:443/omnia/nodes/dde2590f-83cf-46fb-9084-5d88922cdc3d"
payload2  = "{}"

spreadsheet_id = '1QLZ3RZ2QMmwYqwEHncnhymLM0cxOZ233igdSmsP0vjU'
service = build('sheets', 'v4', credentials=creds)

while True:

     try:
        speedtester = speedtest.Speedtest()
        speedtester.get_best_server()
        speed=speedtester.download()/1000000
        
        response = requests.request("POST", url, headers=headers, data = payload)
        response_loads=json.loads(response.text)
        id=(response_loads['sessions'][0]['id'])

        headers2 = {
                'Content-Type': 'application/vnd.alertme.zoo-6.1+json',
                'Accept': 'application/vnd.alertme.zoo-6.1+json',
                'X-Omnia-Client': 'Hive Web Dashboard',
                'X-Omnia-Access-Token': id
        }
        response2 = requests.request("GET", url2, headers=headers2, data=payload2)
        response2_loads=json.loads(response2.text)
        Target_temp=response2_loads['nodes'][0]['attributes']['targetHeatTemperature']['displayValue']
        Curr_temp=response2_loads['nodes'][0]['attributes']['temperature']['displayValue']
        print("Data recieved from Hive")
        
        value_range_body = {
        "majorDimension": "ROWS",
        "values": [
          [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
           sensor.get_temperature(W1ThermSensor.DEGREES_C),
           ldr.value,
           speedtester.download()/8000000,
           Curr_temp,
           Target_temp
          ]
                  ]
        }
        #print("Request ready",value_range_body)
        
        request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range='A1',
                                                          valueInputOption='USER_ENTERED', insertDataOption='INSERT_ROWS', body=value_range_body)
        response = request.execute()
        
        print("Executed at", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        time.sleep(300)
     except:
         print("An exception occurred at", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))



