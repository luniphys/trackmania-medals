# Missing TOTD Gold medals in Trackmania 2020

A little programm regarding the quest of getting every possible Gold medal of every Track of the Day (TOTD) since release. Scrolling through every page in-game plus their loading times takes a while, therefore this programm.

The programm lists all tracks that you're still missing the Gold medal by:

Date, Track name, Time difference: World Record - Gold medal, Your current medal

That list will be printed on the console and also a text file is created on the desktop. In addition a counter of how many and which medals you have gained in total is given at the end.

## How it works

The *tokens.py* file is responsible for getting a Ubisoft ticket with which one receives an access and a refresh token from / for the Nadeo API.
The refresh tokens are used to update the access tokens which usually expire after a short while. The access tokens we can use to call two Nadeo API endpoints: Core & Live.

From these endpoints the programm creates JSON files for every TOTD with their medal times, which are stored locally. So far this is all generic and nothing account related.

To retreive the personal best times (PB's), one needs their account ID. For this the *tokens.py* file has functions that connect to the OAuth Trackmania API in a similar way to how the previous access/ refresh tokens were reveived. In *main.py* we can then use the account ID to make a JSON with every PB for every TOTD.
Since all JSON's carry a lot more information than needed, a final JSON that slices down to only necessary information is made. 

## Use

In general you only need to run *main.py* and log in with ur Ubisoft credentials (once) and it should do everything by itself.

Note that you can only call any mentioned API maximum twice per second as a limit set by Ubisoft. That's why the code execution is paused for 0.5 seconds after every request, to avoid getting banned. Therefore the programm takes a while before it can list your track data. It's only for the first run though (for me about 40s), after that the tracks get listed much quicker (about 3s).

&nbsp;

**Have fun and don't hesitate contacting me if you find a bug or want to comment on something :)**
