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



# For detailed guide getting the OAuth token, visit: https://webservices.openplanet.dev/oauth/auth 

OAuthIdentifier = "b8a9ff146706324ef114"
OAuthSecret = "1add8e1e34a9e68a3374269b5539884d49c186a2"
myWebsite = "https://github.com/luniphys/trackmania-medals"

URL_OAuthCode = f"https://api.trackmania.com/oauth/authorize?response_type=code&client_id={OAuthIdentifier}&redirect_uri={myWebsite}"
# https://api.trackmania.com/oauth/authorize?response_type=code&client_id=b8a9ff146706324ef114&redirect_uri=https://github.com/luniphys/trackmania-medals
# To get the needed authentification code, paste above URL in browser. The redirected URL contains the code.

OAuthCode = "def50200d800acf73ae466fce710f14efe5803dcf76a5c18902baa49ff202ca26eaf45f40a4ea4d2fa30b41c2f5c9ddbd7083e687b54be8a6f539c1c858651f3145a791a0434255587aa5063c7d5befb2db6eaae2266e2ab1c7c1666a9ce6f40aaeedca946d2458df4ed84613632bd89b39c5c7edbef05e8ad67198f4a42a5dec6f5efd15213a3b7784eb7fa54115601dcacddeb593446498c74abeff064b1604059dfdeadc9eeafd29ba0fc453e0412925a0d6b12b7b1957779975f6c27c4e6f4991151f6f9789e7b41572ca0958535f9ab5421afd5cddc049c4febcf091a7c4328d8b3f48819790b3caf5934b2eccc2037871beec70801b350ec8134ab35fafc10bed383570e85dd94b0906833962c440d344a501d7ed60c91303e83b4b861ead5ae054f902ed6d0b32cd256e5b8e90be2a3215134fafbbe7837127631213554fe40e4ef761b5c2fef0212fb4f79a6af4e63406e838afd4a74d21e3fc258f4b0a5f624ecaec003b5785891e244850ee11f52cd426561d36961d6db0607f9f7b161a8a8416df8ffcd2417a892e9aee931fb36912c62d17ae9907fd38985676a71033266498f"
# This code is only valid ONCE!

URL_OAuthToken = "https://api.trackmania.com/api/access_token"
headers_OAuthToken = {"Content-Type": "application/x-www-form-urlencoded"}
# body_OAuthToken = f"grant_type=authorization_code&client_id={OAuthIdentifier}&client_secret={OAuthSecret}&code={OAuthCode}&redirect_uri={myWebsite}"
body_OAuthToken = {"grant_type": "authorization_code",
                   "client_id": f"{OAuthIdentifier}",
                   "client_secret": f"{OAuthSecret}",
                   "code": f"{OAuthCode}",
                   "redirect_uri": f"{myWebsite}"}
response_OAuthToken = req.post(URL_OAuthToken, data=body_OAuthToken, headers=headers_OAuthToken)
print(response_OAuthToken)
response_OAuthToken_JSON = response_OAuthToken.json()
access_OAuthToken = response_OAuthToken_JSON["access_token"]
refresh_OAuthToken = response_OAuthToken_JSON["access_token"]
# Tokens expire after 1 hour!
with open("tokens/access_token_oauth.txt", "w", encoding="utf-8") as file:
            file.write(access_OAuthToken)
with open("tokens/refresh_token_oauth.txt", "w", encoding="utf-8") as file:
            file.write(refresh_OAuthToken)



#TODO: Add refresh token fct for OAuth




with open("tokens/access_token_oauth.txt", "r", encoding="utf-8") as file:
    access_token_oauth = file.read()

url = "https://api.trackmania.com/api/user"
headers = {"Authorization": f"Bearer {access_token_oauth}"}
res = req.get(url, headers=headers)
print(res)
res_JSON = res.json()
print(res_JSON)
