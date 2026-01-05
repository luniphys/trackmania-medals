# Getting all missing TOTD Gold medals in Trackmania 2020

I wrote this little programm regarding my quest to get every possible Gold medal of every Track of the Day (TOTD) since release.
Scrolling through every page in-Game an wait for the medals to load takes a while, therefore this programm.

The tokens.py file is responsible for getting an Ubisoft ticket with which one receives an access and a refresh token from / for the Nadeo API.
The refresh tokens are used to update the access tokens which usually expire after a short while. The access tokens we can use to call two Nadeo API endpoints: Core & Live.

From these endpoints the programm creates JSON files for every TOTD with their medal times, which are stored locally. So far this is all generic and nothing account related.

TO retreive the personal best times (PB'S), one needs his accountID. For this the tokens.py file has functions that connect to OAuth. In main.py we can then use this accountID the make a JSON with every PB for every TOTD.
Since all JSON's carry a lot more information then needed, I made a final JSON that slices down to only all the necessary information. 

Lastly main.py prints and creates a txt file where all tracks are listed that have either a Silver, Bronze medal or aren't driven at all yet.

&nbsp;

&nbsp;

**!!Important for first exection!!**

The programm once ran for the first time runs autonomously, meaning the refreshing part works. However when running it for the first to time, we have a little issue with OAuth, that I can't seem to automate.
For this the user needs to enter the following URL into their browser:

https://api.trackmania.com/oauth/authorize?response_type=code&client_id=b8a9ff146706324ef114&redirect_uri=https://github.com/luniphys/trackmania-medals

Afer login with their Ubisoft account, one gets redirected to this GitHub page with a code in the URL (github.com/trackmania-medals&code=***************)
This code needs to be pastet in for OAuthCode = "..." in the getOAuthCode() function. (line in 214 tokens.py)

Then just execute main.py as normal and it should work!
