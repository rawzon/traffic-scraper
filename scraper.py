import requests
import os
import math

# Constants
RIDE_URL = "https://mdotridedata.state.mi.us/api/v1/organization/michigan_department_of_transportation/dataset/incidents/query?limit=200&_format=json"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MDOT_API_KEY = os.getenv("MDOT_API_KEY")

MONROE_LAT = 41.9403
MONROE_LON = -83.3960
DISTANCE_THRESHOLD_MILES = 40

def havers