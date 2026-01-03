import requests as req
import base64
import json
import datetime as dt
import numpy as np
import math
import time

def getToken(mail, password, live):
    """
    Get authentification tokens for Nadeo API, by first getting ticket from Ubisoft API.
    
    :param mail: Ubisoft login mail adress
    :param password: Ubisoft login password
    :param live: Boolean. True for NadeoLiveServices & False for NadeoServices (Core)
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

    if live:
        body_Nadeo_API = {"audience": "NadeoLiveServices"}
    else:
        body_Nadeo_API = {"audience": "NadeoServices"}

    response_Nadeop_API = req.post(URL_Nadeo_API, headers=headers_Nadeo_API, json=body_Nadeo_API)
    print(response_Nadeop_API)
    response_Nadeop_API_JSON = response_Nadeop_API.json()
    access_token = response_Nadeop_API_JSON["accessToken"]
    refresh_token = response_Nadeop_API_JSON["refreshToken"]

    if live:
        with open("access_token_live.txt", "w", encoding="utf-8") as file:
            file.write(access_token)
        with open("refresh_token_live.txt", "w", encoding="utf-8") as file:
            file.write(refresh_token)
    else:
        with open("access_token_core.txt", "w", encoding="utf-8") as file:
            file.write(access_token)
        with open("refresh_token_core.txt", "w", encoding="utf-8") as file:
            file.write(refresh_token)


def refreshToken(refreshtoken, live):
    """
    Update authentification tokens without the need for re-authenticating the Ubisoft account
    
    :param refreshtoken: Old refresh token 
    :param live: Boolean. True for NadeoLiveServices & False for NadeoServices (Core)
    """
    URL_Refresh = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/refresh"
    headers_Refresh = headers_TOTD = {"Authorization": f"nadeo_v1 t={refreshtoken}"}
    response_Refresh = req.post(URL_Refresh, headers=headers_Refresh)
    print(response_Refresh)
    response_Refresh_JSON = response_Refresh.json()
    access_token = response_Refresh_JSON["accessToken"]
    refresh_token = response_Refresh_JSON["refreshToken"]

    if live:
        with open("access_token_live.txt", "w", encoding="utf-8") as file:
            file.write(access_token)
        with open("refresh_token_live.txt", "w", encoding="utf-8") as file:
            file.write(refresh_token)
    else:
        with open("access_token_core.txt", "w", encoding="utf-8") as file:
            file.write(access_token)
        with open("refresh_token_core.txt", "w", encoding="utf-8") as file:
            file.write(refresh_token)



def getMapInfo(access_token_live):
    """
    Getting map info of all TOTD until today as JSON file
    
    :param token: Nadeo API token
    """
    today = dt.datetime.now()
    release = dt.datetime(2020,7,1)
    months_passed = math.ceil(int(((today-release) / np.timedelta64(1, 'D'))) / 365 * 12)

    URL_TOTD_Maps = f"https://live-services.trackmania.nadeo.live/api/token/campaign/month?length={months_passed}&offset={0}"
    headers_TOTD = {"Authorization": f"nadeo_v1 t={access_token_live}"}

    response_TOTD_Maps = req.get(URL_TOTD_Maps, headers=headers_TOTD)
    print(response_TOTD_Maps)

    maps = response_TOTD_Maps.json()
    with open("mapInfo.json", "w", encoding="utf-8") as file:
        json.dump(maps, file, ensure_ascii=False, indent=4)


def getMapMedals():
    with open("mapInfo.json", "r", encoding="utf-8") as file:
        mapInfo = json.load(file)

    for month in mapInfo["monthList"]:
        for day in month["days"]:
            if day["mapUid"] != "":
                #print(day["monthDay"], month["year"], day["mapUid"])
                pass

    #URL_Records = f"https://live-services.trackmania.nadeo.live/api/token/leaderboard/group/{groupUid}/map/{mapUid}/medals"
    

# Get token as text
with open("credentials.json", "r", encoding="utf-8") as file:
    credentials = json.load(file)
mail = credentials["mail"]
password = credentials["password"]

#getToken(mail, password, True)
#time.sleep(2)
#getToken(mail, password, False)
#time.sleep(2)

#refreshToken(refresh_token_live, True)
#time.sleep(2)
#refreshToken(refresh_token_core, False)
#time.sleep(2)

with open("access_token_live.txt", "r", encoding="utf-8") as file:
    access_token_live = file.read()
with open("access_token_core.txt", "r", encoding="utf-8") as file:
    access_token_core = file.read()
with open("refresh_token_live.txt", "r", encoding="utf-8") as file:
    refresh_token_live = file.read()
with open("refresh_token_core.txt", "r", encoding="utf-8") as file:
    refresh_token_core = file.read()

#getMapInfo(access_token_live)
#time.sleep(2)



#getMapMedals()

URL_Records = f"https://live-services.trackmania.nadeo.live/api/token/leaderboard/group/Personal_Best/map/{"THC2KWupo3WpF_aM2KnJiOwW2zb"}/medals" # 24/2023
headers_Records = {"Authorization": f"nadeo_v1 t={access_token_live}"}
response_Records = req.get(URL_Records, headers=headers_Records)
print(response_Records)
records = response_Records.json()
print(records)
