import requests as req
import base64
import json
import datetime as dt
import numpy as np
import math

def getToken(mail, password):
    """
    Get authentification token for Nadeo API, by first getting ticket from Ubisoft API.
    
    :param mail: Ubisoft login mail adress
    :param password: Ubisoft login password
    """
    # Authentification Ubisoft Account
    URL_Ubisoft_ticket = "https://public-ubiservices.ubi.com/v3/profiles/sessions"

    login = base64.b64encode(f"{mail}:{password}".encode()).decode()
    headers_Ubisoft_ticket = {"Content-Type": "application/json",
                              "Ubi-AppId": "86263886-327a-4328-ac69-527f0d20a237",
                              "Authorization": f"Basic {login}",
                              "User-Agent": f"Getting all maps with missing gold medal / {mail}"}

    response_Ubisoft_ticket = req.post(URL_Ubisoft_ticket, headers=headers_Ubisoft_ticket)
    print(response_Ubisoft_ticket)
    response_Ubisoft_JSON = response_Ubisoft_ticket.json()
    ticket = response_Ubisoft_JSON["ticket"]

    # Authentification Nadeo API
    URL_Nadeo_API = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices"
    headers_Nadeo_API = {"Content-Type": "application/json",
                        "Authorization": f"ubi_v1 t={ticket}",
                        "User-Agent": f"Getting all maps with missing gold medal / {mail}"}

    body_Nadeo_API = {"audience": "NadeoLiveServices"}

    response_Nadeop_API = req.post(URL_Nadeo_API, headers=headers_Nadeo_API, json=body_Nadeo_API)
    print(response_Nadeop_API)
    response_Nadeop_API_JSON = response_Nadeop_API.json()
    token = response_Nadeop_API_JSON["accessToken"]

    with open("token.txt", "w", encoding="utf-8") as file:
        file.write(token)


def getMaps(token):
    """
    Getting map info of all TOTD until today as JSON file
    
    :param token: Nadeo API token
    """
    today = dt.datetime.now()
    release = dt.datetime(2020,7,1)
    months_passed = math.ceil(int(((today-release) / np.timedelta64(1, 'D'))) / 365 * 12)

    URL_TOTD_Maps = f"https://live-services.trackmania.nadeo.live/api/token/campaign/month?length={months_passed}&offset={0}"
    headers_TOTD = {"Authorization": f"nadeo_v1 t={token}"}

    response_TOTD_Maps = req.get(URL_TOTD_Maps, headers=headers_TOTD)
    print(response_TOTD_Maps)

    maps = response_TOTD_Maps.json()
    with open("maps.json", "w", encoding="utf-8") as file:
        json.dump(maps, file, ensure_ascii=False, indent=4)
    

# Get token as text
with open("credentials.json", "r") as file:
    credentials = json.load(file)

mail = credentials["mail"]
password = credentials["password"]

#getToken(mail, password)


with open("token.txt", "r", encoding="utf-8") as file:
    token = file.read()

#getMaps(token)
