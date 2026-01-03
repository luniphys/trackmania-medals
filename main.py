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



def getTOTDMaps(access_token_live):
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
    with open("TOTDMaps.json", "w", encoding="utf-8") as file:
        json.dump(maps, file, ensure_ascii=False, indent=4)


def getMapMedals(access_token_core):
    """
    Getting medal times for all TOTD tracks from Nadeo API
    
    :param access_token_core: Authentification token for Core API
    """
    with open("TOTDMaps.json", "r", encoding="utf-8") as file:
        TOTDMaps = json.load(file)

    mapUidLst = list()
    for month in TOTDMaps["monthList"]:
        for day in month["days"]:
            if day["mapUid"] != "":
                #print(day["monthDay"], month["month"], month["year"], day["mapUid"])
                mapUidLst.append(day["mapUid"])
                
    # len(MapUidLst) > 2000. API only allows list of len < 300. Make parts of 250 elements
    parts = list()
    medalLst = list()
    for i in range(len(mapUidLst)):
        if ((i % 250 == 0 and i != 0) or i == len(mapUidLst) - 1):

            parts.append(mapUidLst[i])

            URL_Medals = f"https://prod.trackmania.core.nadeo.online/maps/by-uid/?mapUidList={",".join(parts)}"
            headers_Medals = {"Authorization": f"nadeo_v1 t={access_token_core}"}
            response_Medals = req.get(URL_Medals, headers=headers_Medals)
            print(response_Medals)
            medals = response_Medals.json()

            for map in medals:
                medalLst.append(map)

            parts = list()
            time.sleep(2)
        else:
            parts.append(mapUidLst[i])
   
    with open("MedalMaps.json", "w", encoding="utf-8") as file:
        json.dump(medalLst, file, ensure_ascii=False, indent=4)

    
def makeJSON():
    """
    Making a final JSON file with only the relevant info.
    """
    with open("TOTDMaps.json", "r", encoding="utf-8") as file:
        TOTDMaps = json.load(file)

    with open("MedalMaps.json", "r", encoding="utf-8") as file:
        MedalMaps = json.load(file)

    finalDict = dict()
    for month in TOTDMaps["monthList"]:
        for day in month["days"]:
            if day["mapUid"] != "":
                finalDict[day["mapUid"]] = {"date": f"{day["monthDay"]}/{month["month"]}/{month["year"]}"}

    for map in MedalMaps:
        finalDict[map["mapUid"]] = {"name": map["name"], "date": finalDict[map["mapUid"]]["date"], "Author": map["authorScore"], "Gold": map["goldScore"], "Silver": map["silverScore"], "Bronze": map["bronzeScore"]}

    with open("Final.json", "w", encoding="utf-8") as file:
        json.dump(finalDict, file, ensure_ascii=False, indent=4)


    

# Get token as text
with open("credentials.json", "r", encoding="utf-8") as file:
    credentials = json.load(file)
mail = credentials["mail"]
password = credentials["password"]

#getToken(mail, password, True)
#time.sleep(1)
#getToken(mail, password, False)
#time.sleep(1)

with open("access_token_live.txt", "r", encoding="utf-8") as file:
    access_token_live = file.read()
with open("access_token_core.txt", "r", encoding="utf-8") as file:
    access_token_core = file.read()
with open("refresh_token_live.txt", "r", encoding="utf-8") as file:
    refresh_token_live = file.read()
with open("refresh_token_core.txt", "r", encoding="utf-8") as file:
    refresh_token_core = file.read()

#refreshToken(refresh_token_live, True)
#time.sleep(1)
#refreshToken(refresh_token_core, False)
#time.sleep(1)


#getTOTDMaps(access_token_live)
#time.sleep(1)

#getMapMedals(access_token_core)
#time.sleep(1)


makeJSON()
time.sleep(1)
