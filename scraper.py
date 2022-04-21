import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional, List
import datetime
import json

session = requests.Session()

# Get session data
request_url = "https://www.dpaonline.co.uk/Calendar-Whats-On"
response = session.get(request_url, verify=False)
html_page_content = BeautifulSoup(response.text, "html.parser")

# Prepare form data for post request
form_data = {
    "__EVENTTARGET": "dnn$ctr2735$XModPro$ctl00$ctl04$rptrListView$ctl02$ctl00$ctl00",
    "__EVENTARGUMENT": "",
    "KB_JSTester_JSEnabled": html_page_content.find("input", {"id": "KB_JSTester_JSEnabled"})["value"],
    "KB_JSTester_JQueryVsn": html_page_content.find("input", {"id": "KB_JSTester_JQueryVsn"})["value"],
    "__VIEWSTATE": html_page_content.find("input", {"id": "__VIEWSTATE"})["value"],
    "__VIEWSTATEGENERATOR": html_page_content.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"],
    "__EVENTVALIDATION": html_page_content.find("input", {"id": "__EVENTVALIDATION"})["value"],
    "dnn$dnnSearch$txtSearch": "",
    "ScrollTop": "",
    "__dnnVariable": html_page_content.find("input", {"id": "__dnnVariable"})["value"],
    "__RequestVerificationToken": html_page_content.find("input", {"name": "__RequestVerificationToken"})["value"],
}

response = session.post(request_url, data=form_data, verify=False)
response_html_page_content = BeautifulSoup(response.text, "html.parser")

    
class Event(BaseModel):
    """Cllass to represent an event"""

    name: Optional[str]
    date_from: Optional[datetime.date]
    date_to: Optional[datetime.date]    
    venue: Optional[str]
    promoter: Optional[str]
    website: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    competition_details: Optional[str]

class Events(BaseModel):
    """Class to hold events (for json conversion)"""

    events: List[Event]

events = response_html_page_content.find("div", {"id": "accordion"})

event_date_names = events.find_all("h4", {"class": "accordion-toggle"})
event_table = events.find_all("div", {"class": "accordion-content"})

data_keys = {
    "Venue:": "venue",
    "Promoter:": "promoter",
    "Mail:": "email",
    "Tel:": "phone",
    "Web:": "website",
    }

unsupported_keys = []

event_objects = []

for i in range(0, len(event_date_names)):

    table_rows = event_table[i].find_all("tr")

    # Get and format the date string
    date_string_split = event_date_names[i].text.split("-")[0].split("to")
    date_from_string_split = date_string_split[0].strip().split(".")
    
    date_to_string_split = None
    if len(date_string_split) > 1:
        date_to_string_split = date_string_split[1].strip().split(".")

    event_data = {}
    event_data["date_from"] = datetime.date(int("20" + date_from_string_split[2]),int(date_from_string_split[1]),int(date_from_string_split[0]))

    if date_to_string_split:
        event_data["date_to"] = datetime.date(int("20" + date_to_string_split[2]),int(date_to_string_split[1]),int(date_to_string_split[0]))
    else:
        event_data["date_to"] = None

    # Get event name
    event_data["name"] = event_date_names[i].text.split("-")[1].strip()

    # Create event data dict to be used to create event object
    for table_row in table_rows:
        table_row_data = table_row.find_all("td")

        data_key = table_row_data[0].text.strip()

        if data_key in data_keys:
            event_data[data_keys[data_key]] = table_row_data[1].text.strip()
        else:
            if data_key not in unsupported_keys:
                unsupported_keys.append(data_key)
                
            event_data[data_key] = table_row_data[1].text.strip()

    event_objects.append(Event(**event_data))

print("\nunsupported_keys:",unsupported_keys)

events_object = Events(events=event_objects)
print(events_object.json())







