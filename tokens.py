import base64
import requests as req
import json



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
    print("Ubisoft Ticket:", response_Ubisoft_ticket)

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
    print("Nadeo Authentification:", response_Nadeop_API)

    response_Nadeop_API_JSON = response_Nadeop_API.json()
    access_token = response_Nadeop_API_JSON["accessToken"]
    refresh_token = response_Nadeop_API_JSON["refreshToken"]

    if live:
        with open("tokens/access_token_live.txt", "w", encoding="utf-8") as file:
            file.write(access_token)
        with open("tokens/refresh_token_live.txt", "w", encoding="utf-8") as file:
            file.write(refresh_token)

    else:
        with open("tokens/access_token_core.txt", "w", encoding="utf-8") as file:
            file.write(access_token)
        with open("tokens/refresh_token_core.txt", "w", encoding="utf-8") as file:
            file.write(refresh_token)



def refreshToken(refreshtoken, live):

    """
    Update authentification tokens without the need for re-authenticating the Ubisoft account
    
    :param refreshtoken: Old refresh token 
    :param live: Boolean. True for NadeoLiveServices & False for NadeoServices (Core)
    """

    URL_Refresh = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/refresh"
    headers_Refresh = {"Authorization": f"nadeo_v1 t={refreshtoken}"}
    
    response_Refresh = req.post(URL_Refresh, headers=headers_Refresh)
    print("Nadeo Refresh:", response_Refresh)

    response_Refresh_JSON = response_Refresh.json()
    access_token = response_Refresh_JSON["accessToken"]
    refresh_token = response_Refresh_JSON["refreshToken"]

    if live:
        with open("tokens/access_token_live.txt", "w", encoding="utf-8") as file:
            file.write(access_token)
        with open("tokens/refresh_token_live.txt", "w", encoding="utf-8") as file:
            file.write(refresh_token)

    else:
        with open("tokens/access_token_core.txt", "w", encoding="utf-8") as file:
            file.write(access_token)
        with open("tokens/refresh_token_core.txt", "w", encoding="utf-8") as file:
            file.write(refresh_token)



# Get tokens
with open("credentials.json", "r", encoding="utf-8") as file:
    credentials = json.load(file)
mail = credentials["mail"]
password = credentials["password"]

#getToken(mail, password, True)
#time.sleep(2)
#getToken(mail, password, False)
#time.sleep(2)


# Refresh tokens
with open("tokens/refresh_token_live.txt", "r", encoding="utf-8") as file:
    refresh_token_live = file.read()
with open("tokens/refresh_token_core.txt", "r", encoding="utf-8") as file:
    refresh_token_core = file.read()

#refreshToken(refresh_token_live, True)
#time.sleep(2)
#refreshToken(refresh_token_core, False)
#time.sleep(2)



OAuthIdentifier = "b8a9ff146706324ef114"
myWebsite = "x"
URL = f"https://api.trackmania.com/oauth/authorize?response_type=code&client_id={OAuthIdentifier}&redirect_uri={myWebsite}"


URL_OAuth = "https://api.trackmania.com/api/user"
headers_OAuth = {"Authorization": f"Bearer {token}"}
