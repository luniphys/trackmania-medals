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

    if not os.path.isfile("tokens/access_token_core.txt") or not os.path.isfile("tokens/access_token_live.txt"):
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

    OAuthCode = "def502007e126b95ec83a8ed7ad420ebc2a937288e8afcfbbef30e86f88a33617fd47a9f9f55dfa85f9d704b72cb8d01be51a70d1986381e19438bc23bc9db75d04a12073eef0b9bf21af379272169e5db662c8db296a264f03db98ea6a57ddb4068a4378f5f831b22d6341a239a6fb6a541012392f4a223ad95a4085b9870382a139c02a37d9f2430184bb39bfafa9a737773e4a84e7d3d698425dbfc653836c685b98e7a5a351f648cb26309b62c15a36a068c34ff0eb4e52f4560cbc9818aa1b812ef6ef1dc8bf68d8557890c7879e2ca0392487ea8ce02df87405d009a7408cf0bd521e30ec652444d264b5a65ca4aff878534b4add8a519383b590a6f0784878ac02365b6d0124a88cbdcdedb424a2ca5592dbafa4a99f295c8efd75c04a6d6e50ebb516719ded8ca5ff264300a3c807b00d6e5a571113dd0fcba454e38bd1d599625f114f251688e328721eb84fffbab68428134361a413297ddf7cc49f28f9462411900ed33642b28513f038f5a6dd07b6f9ecad2fdf2a89061f9dae0866db8598f33578c78198047dafecd4de80f0609126f23189af330f69194d965ec4fe7e38b92"
    # This code is only valid ONCE!

    return OAuthCode



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

if not os.path.isfile("accountId"):
    getAccountId()
