import requests as req
import json
import datetime as dt
import numpy as np
import math
import time


def getTOTDMaps():

    """
    Getting map info of all TOTD until today as JSON file
    """

    with open("tokens/access_token_live.txt", "r", encoding="utf-8") as file:
        access_token_live = file.read()

    today = dt.datetime.now()
    release = dt.datetime(2020,7,1)
    months_passed = math.ceil(int(((today-release) / np.timedelta64(1, 'D'))) / 365 * 12)

    URL_TOTD_Maps = f"https://live-services.trackmania.nadeo.live/api/token/campaign/month?length={months_passed}&offset={0}"
    headers_TOTD = {"Authorization": f"nadeo_v1 t={access_token_live}"}
    response_TOTD_Maps = req.get(URL_TOTD_Maps, headers=headers_TOTD)
    print("Nadeo TOTD:", response_TOTD_Maps)

    maps = response_TOTD_Maps.json()
    with open("TOTDMaps.json", "w", encoding="utf-8") as file:
        json.dump(maps, file, ensure_ascii=False, indent=4)



def getMapMedals():

    """
    Getting medal times for all TOTD tracks from Nadeo API
    """

    with open("tokens/access_token_core.txt", "r", encoding="utf-8") as file:
        access_token_core = file.read()

    with open("TOTDMaps.json", "r", encoding="utf-8") as file:
        TOTDMaps = json.load(file)

    mapUidLst = list()
    for month in TOTDMaps["monthList"]:
        for day in month["days"]:
            if day["mapUid"] != "":
                mapUidLst.append(day["mapUid"])
                
    # len(MapUidLst) > 2000. API only allows list of len < 300. Make parts of 250 elements:

    parts = list()
    medalLst = list()

    for i in range(len(mapUidLst)):

        if ((i % 250 == 0 and i != 0) or i == len(mapUidLst) - 1):

            parts.append(mapUidLst[i])

            URL_Medals = f"https://prod.trackmania.core.nadeo.online/maps/by-uid/?mapUidList={",".join(parts)}"
            headers_Medals = {"Authorization": f"nadeo_v1 t={access_token_core}"}

            response_Medals = req.get(URL_Medals, headers=headers_Medals)
            print("Nadeo Medals:", response_Medals)

            medals = response_Medals.json()

            for map in medals:
                medalLst.append(map)

            parts = list()
            time.sleep(2)

        else:
            parts.append(mapUidLst[i])
   
    with open("MedalMaps.json", "w", encoding="utf-8") as file:
        json.dump(medalLst, file, ensure_ascii=False, indent=4)



def getPersonalRecords(tokiii):
    pass



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
        finalDict[map["mapUid"]] = {"name": map["name"], "date": finalDict[map["mapUid"]]["date"], "mapId": map["mapId"], "Author": map["authorScore"], "Gold": map["goldScore"], "Silver": map["silverScore"], "Bronze": map["bronzeScore"]}

    with open("Final.json", "w", encoding="utf-8") as file:
        json.dump(finalDict, file, ensure_ascii=False, indent=4)



# Get Map Info JSON's
#getTOTDMaps()
#time.sleep(2)

#getMapMedals()
#time.sleep(2)

#makeJSON()



mapUid  = "89I3ZHH0qhCtGYfX3vOf90jz2h4"             # 4/7/2022
mapId   = "80302944-b40d-4cf8-b25a-00c4824606ed"    # 4/7/2022

