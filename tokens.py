import base64
import requests as req
import json
import time
import os


def getCredent():

    """
    Small function for user to enter Ubisoft login mail & password, which is needed for Ubisoft ticket.
    """

    print("Please Enter your Ubisoft Login Email and Password.")
    mail = input("Email: ")

    sure = False
    while sure == False:
        print(f"Are you sure \'{mail}\' is correct? [y/n]")
        ans = input()
        if ans == "y":
            sure = True
        else:
            mail = input("Email: ")


    password = input("Password: ")

    sure = False
    while sure == False:
        print(f"Are you sure \'{password}\' is correct? [y/n]")
        ans = input()
        if ans == "y":
            sure = True
        else:
            mail = input("Password: ")


    credentials = {"mail": mail, "password": password}
    with open("credentials.json", "w", encoding="utf-8") as file:
        json.dump(credentials, file, ensure_ascii=False, indent=4)



def getToken():

    """
    Get authentification tokens for Nadeo API, by first getting ticket from Ubisoft API.
    """

    if not os.path.isfile("credentials.json"):
        getCredent()

    with open("credentials.json", "r", encoding="utf-8") as file:
        credentials = json.load(file)

    mail = credentials["mail"]
    password = credentials["password"]


    # Authentification Ubisoft Account
    URL_Ubisoft_ticket = "https://public-ubiservices.ubi.com/v3/profiles/sessions"

    login = base64.b64encode(f"{mail}:{password}".encode()).decode()
    headers_Ubisoft_ticket = {"Content-Type": "application/json",
                              "Ubi-AppId": "86263886-327a-4328-ac69-527f0d20a237",
                              "Authorization": f"Basic {login}",
                              "User-Agent": f"Getting all maps with missing gold medal / {mail}"}

    response_Ubisoft_ticket = req.post(URL_Ubisoft_ticket, headers=headers_Ubisoft_ticket)
    print("Ubisoft Ticket:", response_Ubisoft_ticket)
    time.sleep(2)

    response_Ubisoft_JSON = response_Ubisoft_ticket.json()

    try:
        ticket = response_Ubisoft_JSON["ticket"]

    except:
        print(response_Ubisoft_JSON)
        return 0

    def getNadeoToken(ticket, mail, live):

        """
        Docstring for getNadeoToken
        
        :param ticket: Ubisoft ticket
        :param mail: Ubisoft login mail address for user agent header
        :param live: Wether to get token for NadeoLiveServices (True) or NadeoServices (False)
        """

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
        time.sleep(2)

        response_Nadeop_API_JSON = response_Nadeop_API.json()

        try:
            access_token = response_Nadeop_API_JSON["accessToken"]
            refresh_token = response_Nadeop_API_JSON["refreshToken"]
        
        except:
             print(response_Nadeop_API_JSON)
             return 0

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


    getNadeoToken(ticket, mail, True)
    getNadeoToken(ticket, mail, False)



def refreshToken():

    """
    Update authentification tokens without the need for re-authenticating the Ubisoft account
    """
    
    if not os.path.exists("tokens"):
         os.mkdir("tokens")

    if not os.path.isfile("tokens/access_token_core") or not os.path.isfile("tokens/access_token_live"):
         getToken()
         return None
    

    def getRefreshToken(refreshtoken, live):

        """
        Getting the tokens
        
        :param refreshtoken: Old refresh token 
        :param live: Wether to get token for NadeoLiveServices (True) or NadeoServices (False)
        """

        URL_Refresh = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/refresh"
        headers_Refresh = {"Authorization": f"nadeo_v1 t={refreshtoken}"}
        
        response_Refresh = req.post(URL_Refresh, headers=headers_Refresh)
        print("Nadeo Refresh:", response_Refresh)
        time.sleep(2)

        response_Refresh_JSON = response_Refresh.json()

        try:
            access_token = response_Refresh_JSON["accessToken"]
            refresh_token = response_Refresh_JSON["refreshToken"]

        except:
             print(response_Refresh_JSON)
             return 0

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


    with open("tokens/refresh_token_live.txt", "r", encoding="utf-8") as file:
        refresh_token_live = file.read()

    with open("tokens/refresh_token_core.txt", "r", encoding="utf-8") as file:
        refresh_token_core = file.read()

    getRefreshToken(refresh_token_live, True)
    getRefreshToken(refresh_token_core, False)



def getOAuthToken(OAuthCode):

    """
    Get OAuth Authentification Token to retreive accountId from Nadeo API
    
    :param OAuthCode: OAuth code need to get the tokens
    """
    OAuthIdentifier = "b8a9ff146706324ef114"
    OAuthSecret = "1add8e1e34a9e68a3374269b5539884d49c186a2"
    myWebsite = "https://github.com/luniphys/trackmania-medals"

    URL_OAuthToken = "https://api.trackmania.com/api/access_token"
    headers_OAuthToken = {"Content-Type": "application/x-www-form-urlencoded"}
    body_OAuthToken = {"grant_type": "authorization_code",
                       "client_id": f"{OAuthIdentifier}",
                       "client_secret": f"{OAuthSecret}",
                       "code": f"{OAuthCode}",
                       "redirect_uri": f"{myWebsite}"}
    
    response_OAuthToken = req.post(URL_OAuthToken, data=body_OAuthToken, headers=headers_OAuthToken)
    print("OAuth Authentification:", response_OAuthToken)
    time.sleep(2)

    response_OAuthToken_JSON = response_OAuthToken.json()

    try:
        access_OAuthToken = response_OAuthToken_JSON["access_token"]
        refresh_OAuthToken = response_OAuthToken_JSON["refresh_token"]
    except:
         print(response_OAuthToken_JSON)
         return 0

    # Access token expire after 1 hour! Refresh tokens last 1 month.

    with open("tokens/access_token_oauth.txt", "w", encoding="utf-8") as file:
                file.write(access_OAuthToken)
    with open("tokens/refresh_token_oauth.txt", "w", encoding="utf-8") as file:
                file.write(refresh_OAuthToken)



def getOAuthCode():

    """
    Function for getting the OAuth Code. For now has to be done manually within a browser. Implementation migth follow if possible.
    For a detailed guide getting the OAuth token, visit: https://webservices.openplanet.dev/oauth/auth
    """
 
    OAuthIdentifier = "b8a9ff146706324ef114"
    myWebsite = "https://github.com/luniphys/trackmania-medals"

    URL_OAuthCode = f"https://api.trackmania.com/oauth/authorize?response_type=code&client_id={OAuthIdentifier}&redirect_uri={myWebsite}"
    # https://api.trackmania.com/oauth/authorize?response_type=code&client_id=b8a9ff146706324ef114&redirect_uri=https://github.com/luniphys/trackmania-medals
    # To get the needed authentification code, paste above URL in browser. The redirected URL contains the code.

    OAuthCode = "def50200376ad80eb3b58aaf082573a1a1ba25a67badf7a151580fd7431d4702be96e97c92ab14ee870263fe55adb851e46ba67d8b40061ab41ce8cd6676a5182cb93d88bacd5b3c5b01a03523a34da9629d4a12d5cc0c0cb9cd84d78de465816be55fc12d944baa4a64ea0f82afe0ddb31d06dd3be8f5193947bda803f6d4008e256ee5f288f5a025d526cb742493e9401671757ae04e1ad3f91333dbc54e0d21cfd36a5cb863f001014a4ec045dad3318fa4328286d9be16c2d487765ac0da3e15ad40146be2ce813ed5239b404133168fcafc3b69dc5752942de8ab6132e6a1beb87f8fef28d51f169414819ee7ad7190cca2cb65443f34060421f134853004a79798ffb9a40647ec6fadd3ac9f4c9d0032373475326a799e8a9377edaefb2162655db40e7468d6cf95abc0a3f109b28f207b0ed2a4ec6fddc48adcf699b755010c38698121b3679e671e9aac2affc6a8188bb211af9042f6bc1f117f41d2a4f701c281ab76fdeaf1b50ea27b86daa15b24ba0106a27f975de165688e8cbe0dbb37cb2913f47070077dc36ca310e1a9d509dc80f73bd780454e689a841e5c06e670c2d933"
    # This code is only valid ONCE!

    return OAuthCode



def refreshOAuthToken():

    """
    Refresh OAuth Authentification tokens.
    """

    if not os.path.exists("tokens"):
         os.mkdir("tokens")

    if not os.path.isfile("tokens/access_token_oauth.txt"):
         OAuthCode = getOAuthCode()
         getOAuthToken(OAuthCode)
         return None
    

    with open("tokens/refresh_token_oauth.txt", "r", encoding="utf-8") as file:
        refreshtoken = file.read()

    OAuthIdentifier = "b8a9ff146706324ef114"
    OAuthSecret = "1add8e1e34a9e68a3374269b5539884d49c186a2"

    URL_OAuthToken = "https://api.trackmania.com/api/access_token"
    headers_OAuthToken = {"Content-Type": "application/x-www-form-urlencoded"}
    body_OAuthToken = {"grant_type": "refresh_token",
                       "client_id": f"{OAuthIdentifier}",
                       "client_secret": f"{OAuthSecret}",
                       "refresh_token": f"{refreshtoken}"}
    
    response_OAuthToken = req.post(URL_OAuthToken, data=body_OAuthToken, headers=headers_OAuthToken)
    print("OAuth Refresh:", response_OAuthToken)
    time.sleep(2)

    response_OAuthToken_JSON = response_OAuthToken.json()

    try:
        access_OAuthToken = response_OAuthToken_JSON["access_token"]
        refresh_OAuthToken = response_OAuthToken_JSON["refresh_token"]
    
    except:
         print(response_OAuthToken_JSON)
         return 0

    # Access token expire after 1 hour! Refresh tokens last 1 month.

    with open("tokens/access_token_oauth.txt", "w", encoding="utf-8") as file:
                file.write(access_OAuthToken)
    with open("tokens/refresh_token_oauth.txt", "w", encoding="utf-8") as file:
                file.write(refresh_OAuthToken)



def getAccountId():
    
    """
    Getting the AccountId saved as txt file
    """

    if not os.path.isfile("accountId.txt"):

        with open("tokens/access_token_oauth.txt", "r", encoding="utf-8") as file:
            access_token_oauth = file.read()

        URL_accountId = "https://api.trackmania.com/api/user"
        headers_accountId = {"Authorization": f"Bearer {access_token_oauth}"}

        response_accountId = req.get(URL_accountId, headers=headers_accountId)
        print("OAuth AccountId", response_accountId)
        time.sleep(2)

        response_accountId_JSON = response_accountId.json()

        try:
            accountId = response_accountId_JSON["accountId"]
        
        except:
             print(response_accountId_JSON)
             return 0

        with open("accountId.txt", "w", encoding="utf-8") as file:
            file.write(accountId)



refreshToken()

refreshOAuthToken()

getAccountId()
