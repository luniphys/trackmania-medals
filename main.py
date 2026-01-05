import requests as req
import json
import datetime as dt
import numpy as np
import math
import time
import os
import re
import shutil

from tokens import *


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
    time.sleep(2)

    maps = response_TOTD_Maps.json()

    if not os.path.exists("MapJSONs"):
        os.mkdir("MapJSONs")

    with open("MapJSONs/TOTDMaps.json", "w", encoding="utf-8") as file:
        json.dump(maps, file, ensure_ascii=False, indent=4)



def getMapMedals():

    """
    Getting medal times for all TOTD tracks from Nadeo API
    """

    with open("tokens/access_token_core.txt", "r", encoding="utf-8") as file:
        access_token_core = file.read()

    with open("MapJSONs/TOTDMaps.json", "r", encoding="utf-8") as file:
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
            time.sleep(2)

            medals = response_Medals.json()

            for map in medals:
                medalLst.append(map)

            parts = list()

        else:
            parts.append(mapUidLst[i])
   
    with open("MapJSONs/MedalMaps.json", "w", encoding="utf-8") as file:
        json.dump(medalLst, file, ensure_ascii=False, indent=4)



def getPersonalRecords():
    """
    Get the personal bests for every track. If track is not driven yet API returns nothing!
    """
    with open("tokens/access_token_core.txt", "r", encoding="utf-8") as file:
        access_token_core = file.read()

    with open("MapJSONs/MedalMaps.json", "r", encoding="utf-8") as file:
        MedalMaps = json.load(file)

    with open("accountId.txt", "r", encoding="utf-8") as file:
        accId = file.read()

    mapIdLst = list()
    for track in MedalMaps:
        mapIdLst.append(track["mapId"])

    # len(MapIdLst) > 2000. API only allows list of len < 200. Make parts of 150 elements:

    parts = list()
    PersRecLst = list()

    for i in range(len(mapIdLst)):

        if ((i % 150 == 0 and i != 0) or i == len(mapIdLst) - 1):

            parts.append(mapIdLst[i])

            URL_PBs = f"https://prod.trackmania.core.nadeo.online/v2/accounts/{accId}/mapRecords?mapIdList={",".join(parts)}"
            headers_PBs = {"Authorization": f"nadeo_v1 t={access_token_core}"}

            response_PBs = req.get(URL_PBs, headers=headers_PBs)
            print("Nadeo PBs:", response_PBs)
            time.sleep(2)

            PB = response_PBs.json()

            for map in PB:
                PersRecLst.append(map)

            parts = list()

        else:
            parts.append(mapIdLst[i])


    with open("MapJSONs/PBMaps.json", "w", encoding="utf-8") as file:
        json.dump(PersRecLst, file, ensure_ascii=False, indent=4)



def makeJSON():

    """
    Making a final JSON file with only the relevant info.
    """

    with open("MapJSONs/TOTDMaps.json", "r", encoding="utf-8") as file:
        TOTDMaps = json.load(file)

    with open("MapJSONs/MedalMaps.json", "r", encoding="utf-8") as file:
        MedalMaps = json.load(file)

    with open("MapJSONs/PBMaps.json", "r", encoding="utf-8") as file:
        PBMaps = json.load(file)

    finalDict = dict()
    for month in TOTDMaps["monthList"]:
        for day in month["days"]:
            if day["mapUid"] != "":
                finalDict[day["mapUid"]] = {"date": f"{day["monthDay"]}/{month["month"]}/{month["year"]}"}

    for map in MedalMaps:
        finalDict[map["mapUid"]] = {"name": map["name"], "date": finalDict[map["mapUid"]]["date"], "mapId": map["mapId"], "Author": map["authorScore"] / 1000, "Gold": map["goldScore"] / 1000, "Silver": map["silverScore"] / 1000, "Bronze": map["bronzeScore"] / 1000}

    for mapFin in finalDict:
        for (i, mapPB) in enumerate(PBMaps):

            if finalDict[mapFin]["mapId"] == mapPB["mapId"]:
                finalDict[mapFin]["medal"] = mapPB["medal"]
                finalDict[mapFin]["Pers. Best"] = mapPB["recordScore"]["time"] / 1000
                finalDict[mapFin]["mapRecordId"] = mapPB["mapRecordId"]
                break

            if i == len(PBMaps) - 1 and finalDict[mapFin]["mapId"] != mapPB["mapId"]: # For tracks that haven't been driven yet
                finalDict[mapFin]["medal"] = 0
                finalDict[mapFin]["Pers. Best"] = None
                finalDict[mapFin]["mapRecordId"] = None

        
    with open("MapJSONs/Final.json", "w", encoding="utf-8") as file:
        json.dump(finalDict, file, ensure_ascii=False, indent=4)



def getWorldRecord(mapUid):

    """
    Return the world record time for a given mapUid 
    
    :param mapUid: map identifier
    :return WR: world record time
    """

    with open("tokens/access_token_live.txt", "r", encoding="utf-8") as file:
        access_token_live = file.read()

    URL_WR = f"https://live-services.trackmania.nadeo.live/api/token/leaderboard/group/Personal_Best/map/{mapUid}/top?length=1&onlyWorld=true"
    headers_WR = {"Authorization": f"nadeo_v1 t={access_token_live}"}

    response_WR = req.get(URL_WR, headers=headers_WR)
    #print("Nadeo WR:", response_WR)
    time.sleep(2)

    response_WR_JSON = response_WR.json()
    WR = response_WR_JSON["tops"][0]["top"][0]["score"]

    return WR / 1000




def printInfo():

    """
    Printing the missing gold medal maps & some overall medal info 
    """
    
    def clearTMnames(title):

        """
        Remove all the color and style codes within the titles of a map
        
        :param title: Titel of map
        """

        placeholder = "\0"
        title = title.replace("$$", placeholder)

        title = re.sub(r"\$[0-9a-fA-F]{3}", "", title)  # Farben
        title = re.sub(r"\$[a-zA-Z]", "", title)        # Styles

        return title.replace(placeholder, "$")
    


    with open("MapJSONs/Final.json", "r", encoding="utf-8") as file:
        FinalMaps = json.load(file)

    if os.path.isfile("medals.txt"):
        os.remove("medals.txt")

    countDict = dict()
    print()

    for map in FinalMaps:

        if FinalMaps[map]["medal"] < 3:
            
            s = f"{FinalMaps[map]["date"]}, {clearTMnames(FinalMaps[map]["name"])}, WR-Gold delta: {round(FinalMaps[map]["Gold"] - getWorldRecord(map), 3)}, "
            
            if FinalMaps[map]["medal"] == 2:
                s += "Silver"

            elif FinalMaps[map]["medal"] == 1:
                s += "Bronze"

            else:
                s += "No medal"


            print(s + "\n")
        
            with open("medals.txt" , "a", encoding="utf-8") as file:
                file.write(s + "\n")

        countDict[FinalMaps[map]["medal"]] = countDict.get(FinalMaps[map]["medal"], 0) + 1


    freq = f"\nAuthor: {countDict[4]}, Gold: {countDict[3]}, Silver: {countDict[2]}, Bronze: {countDict[1]}, No mdeal: {countDict[0]}\n"
    
    print(freq)
    with open("medals.txt" , "a", encoding="utf-8") as file:
                file.write(freq)
    




today = str(dt.datetime.now().date())

if not os.path.isfile("lastUpdate.txt"):
    with open("lastUpdate.txt", "w", encoding="utf-8") as file:
        file.write(today)

with open("lastUpdate.txt", "r", encoding="utf-8") as file:
        lastUpdate = file.read()

if today != lastUpdate or not os.path.isfile("lastUpdate.txt") or not os.path.exists("MapJSONs"):

    with open("lastUpdate.txt", "w", encoding="utf-8") as file:
        file.write(today)

    getTOTDMaps()
    getMapMedals()
    getPersonalRecords()
    makeJSON()


printInfo()

shutil.copy("medals.txt", "C:/Users/lunip/Desktop/medals.txt")
