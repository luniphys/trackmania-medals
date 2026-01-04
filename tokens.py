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

    OAuthCode = "def502000c0d84a9ebff5274c491b81c43feabf9670d195aceddbc2b581c13503908ae1f5b30a4b0fe41a441a8377a19beedd420d4cfd0409ef8076713643097d3e08745ce58481a94d5dd8bcf2a4d97506beed19493c7c557787cacb022948ea8ffc31fbe5783c7867b250aa4527d6cca2a414db42e1d6076ad1ad641fc35bc6738dae75b3ce860da4202421cf8804263ae12bd67a9f296fe0ffd3762d6cc157fabb1def6356a95cb6dc015c75bbf881df8a3162bf0556c3ff5a666812667d40bfb7dad2a350c353efa4802ec31541149e2456747293d93fb50f3e63c98efc821516582256699934e9efefb068cc250a217e04353656616530a375abd719eec0eafca0f50fed802043fc8985e6f6bcb163996d922488babe8edfad7e8077453c7fb0abe6d9ddec2dd81a13ba0fc74c8ba2061e88d6f39f98a8bd1d390172779956413d74c3d2fd9e63e84c8c6ff18ba7eb8958f291185b7def609ed68a084dc78a70269ed9412547bfc22b5d667eb03e4cd05c6c62eedfe4e9d5ccc82d20672a430b0d10f32bdcb2eae213677faae5bd448415d5a92c426af1400d81b098a8917b2e8cd7917"
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

if not os.path.isfile("accountId"):
    getAccountId()
