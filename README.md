# Getting all missing TOTD Gold medals in Trackmania 2020

I wrote this little programm regarding my quest to get every possible Gold medal of every Track of the Day (TOTD) since release.
Scrolling through every page in-Game an wait for the medals to load takes a while, therefore this programm.

The tokens.py file is responsible for getting a Ubisoft ticket with which one receives an access and a refresh token from / for the Nadeo API.
The refresh tokens are used to update the access tokens which usually expire after a short while. The access tokens we can use to call two Nadeo API endpoints: Core & Live.

From these endpoints the programm creates JSON files for every TOTD with their medal times, which are stored locally. So far this is all generic and nothing account related.

TO retreive the personal best times (PB'S), one needs his accountID. For this the tokens.py file has functions that connect to OAuth Trackmania API. In main.py we can then use this accountID the make a JSON with every PB for every TOTD.
Since all JSON's carry a lot more information then needed, I made a final JSON that slices down to only all the necessary information. 

In general you only need to run main.py and it should create a txt file where all tracks are listed that have either a Silver, Bronze medal or aren't driven at all yet.

&nbsp;

**Have fun and don't hesitate contacting me if you find a bug or something is not working :)**
