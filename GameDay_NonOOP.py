#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 22:06:52 2022

@author: christopherquintas
"""
import pandas as pd
import numpy as np
import requests
import statsapi
import json
from datetime import date
import re

stadium_info = [{"team":"Los Angeles Angels","address":"2000 Gene Autry Way, Anaheim, CA. 92806","lat":33.799572,"lng":-117.889031},
                {"team":"Arizona Diamondbacks","address":"P.O. Box 2095, Phoenix, AZ. 85001","lat":33.452922,"lng":-112.038669},
                {"team":"Atlanta Braves","address":"P.O. Box 4064, Atlanta, GA. 30302","lat":33.74691,"lng":-84.391239},
                {"team":"Baltimore Orioles","address":"333 W. Camden Street, Baltimore, MD. 21201","lat":39.285243,"lng":-76.620103},
                {"team":"Boston Red Sox","address":"4 Yawkey Way, Boston, MA 02215","lat":42.346613,"lng":-71.098817},
                {"team":"Chicago Cubs","address":"1060 Addison Street, Chicago, IL 60616","lat":41.947201,"lng":-87.656413},
                {"team":"Chicago White Sox","address":"333 W. 35th Street, Chicago, IL 60616","lat":41.830883,"lng":-87.635083},
                {"team":"Cincinnati Reds","address":"100 Cinergy Field, Cincinnati, OH 45202","lat":39.107183,"lng":-84.507713},
                {"team":"Cleveland Guardians","address":"2401 Ontario Street, Cleveland, OH 44115","lat":41.495149,"lng":-81.68709},
                {"team":"Colorado Rockies","address":"Coors Field, 2001 Blake Street, Denver, CO 80205-2000","lat":39.75698,"lng":-104.965329},
                {"team":"Detroit Tigers","address":"Comerica Park, 2100 Woodward Ave., Detroit, MI 48201","lat":42.346354,"lng":-83.059619},
                {"team":"Miami Marlins","address":"2269 NW 199th Street, Miami, FL 33056","lat":25.954428,"lng":-80.238164},
                {"team":"Houston Astros","address":"P.O. Box 288, Houston, TX 77001-0288","lat":29.76045,"lng":-95.369784},
                {"team":"Kansas City Royals","address":"P.O. Boz 419969, Kansas City, MO 64141","lat":39.10222,"lng":-94.583559},
                {"team":"Los Angeles Dodgers","address":"1000 Elysian Park Ave., Los Angeles, CA 90012","lat":34.072437,"lng":-118.246879},
                {"team":"Milwaukee Brewers","address":"P.O. Box 3099, Milwaukee, WI 53201-3099","lat":43.04205,"lng":-87.905599},
                {"team":"Minnesota Twins","address":"501 Chicago Ave. S., Minneapolis, MN 55415","lat":44.974346,"lng":-93.259616},
                {"team":"New York Mets","address":"Roosevelt Ave & 126th Street, New York, NY 11368","lat":40.75535,"lng":-73.843219},
                {"team":"New York Yankees","address":"Yankee Stadium, E. 161 Street & River Ave., New York, NY 10451","lat":40.819782,"lng":-73.929939},
                {"team":"Oakland Athletics","address":"Oakland Coliseum, 700 Coliseum Way, Oakland, Ca 94621-1918","lat":37.74923,"lng":-122.196487},
                {"team":"Philadelphia Phillies","address":"P.O. Box 7575, Philadelphia, PA 19101","lat":39.952313,"lng":-75.162392},
                {"team":"Pittsburgh Pirates","address":"600 Stadium Circle, Pittsburgh, PA 15212","lat":40.461503,"lng":-80.008924},
                {"team":"St. Louis Cardinals","address":"250 Stadium Plaza, St. Louis, MO 63102","lat":38.629683,"lng":-90.188247},
                {"team":"San Diego Padres","address":"P.O. Box 2000, San Diego, CA 92112-2000","lat":32.752148,"lng":-117.143635},
                {"team":"San Francisco Giants","address":"Pacific Bell Park, 24 Willie Mays Plaza, San Francisco, CA 94107","lat":37.77987,"lng":-122.389754},
                {"team":"Seattle Mariners","address":"P.O. Box 41000, 411 First Ave. S., Seattle, WA 98104","lat":47.60174,"lng":-122.330829},
                {"team":"Tampa Bay Rays","address":"1 Tropicana Drive, St. Petersburg, FL 33705","lat":27.768487,"lng":-82.648191},
                {"team":"Texas Rangers","address":"1000 Ballpark Way, Arlington, TX 76011","lat":32.750156,"lng":-97.081117},
                {"team":"Toronto Blue Jays","address":"1 Blue Jay Way, Suite 3200, Toronto, ONT M5V 1J1","lat":43.641653,"lng":-79.3917},
                {"team":"Washington Nationals","address":"1500 South Capitol Street SE, Washington, DC","lat":38.87,"lng":-77.01}]

weather_lookup = {
    'clearday': 'Clear Skies',
    'clearnight': 'Clear Skies',
    'pcloudyday': 'Partly Cloudy',
    'pcloudynight': 'Partly Cloudy',
    'mcloudyday': 'Mostly Cloudy',
    'mcloudynight': 'Mostly Cloudy',
    'cloudyday': 'Cloudy',
    'cloudynight': 'Cloudy',
    'humidday': 'Humid, Partly Cloudy',
    'humidnight': 'Humid, Partly Cloudy',
    'lightrainday': 'Light Rain',
    'lightrainnight': 'Light Rain',
    'oshowerday': 'Overcast, Showers',
    'oshowernight': 'Overcast, Showers',
    'ishowerday': 'Showers',
    'ishowernight': 'Showers',
    'lightsnowday': 'Light Snow',
    'lightsnownight': 'Light Snow',
    'rainday': 'Rain',
    'rainnight': 'Rain',
    'snowday': 'Snow',
    'snownight': 'Snow',
    'rainsnowday': 'Freezing Rain',
    'rainsnownight': 'Freezing Rain',
    'tsday': 'Thunderstorms',
    'tsnight': 'Thunderstorms'
}

#get todays date
today = date.today()
today = today.strftime("%m/%d/%Y")

sched = statsapi.schedule(today)

game_DF = pd.DataFrame({"Game":[], "Time" : []})


gameList = []
games_list = []
games_times = []
location_list = []
doubleheader_count = 0
for game in sched:
    home_team = game['home_name']
    away_team = game['away_name']
    location_data = list(filter(lambda team: team['team'] == home_team, stadium_info))[0]
    location_list.append([location_data['lng'], location_data['lat']])

    teams = away_team + " @ " + home_team 
    game_time = game['game_datetime']


    if game['doubleheader'] == 'S':
        if doubleheader_count == 0:
            doubleheader_count = 1
            teams = teams + " Game 1"
        else:
            teams = teams + " Game 2"


    game_time = re.findall('\d{2}:\d{2}', game_time)[0]
    
    hour = int(game_time[:2])

    #Time Change for when games start at [1,5] AM 
    if hour <= 5:
        hour = 24 + hour
        
    hour = hour - 7 #MST     
    min = game_time[3:]
    if hour >= 12:
        std_time =  hour % 12
        if std_time == 0:
            std_time = 12
        game_time = str(std_time) + ':' + min + " PM MST"
    else:
        game_time = str(hour) + ':' + min + " AM MST"
    
    games_list.append(teams)
    games_times.append(game_time)
    gameList.append(home_team + " vs " + away_team + " @ " + game_time)


game_DF["Game"] = games_list
game_DF["Time"] = games_times
game_DF["Location"] = location_list


home_pitcher_list = []
away_pitcher_list = []
for game in sched:
    home_pitcher = game['home_probable_pitcher']
    away_pitcher = game['away_probable_pitcher']
    
    home_pitcher_list.append(home_pitcher)
    away_pitcher_list.append(away_pitcher)


game_DF["Home Pitcher"] = home_pitcher_list
game_DF["Away Pitcher"] = away_pitcher_list


url = "http://www.7timer.info/bin/api.pl?lon={lon}&lat={lat}&product={product}&output={type}"

weather_list = []
#weather = requests.get(url.format(lon=x['lng'], lat=x['lat'], product='civil', type='json')).json()

for location in location_list:
    lon = location[0]
    lat = location[1]
    weather = requests.get(url.format(lon = lon, lat = lat, product='civil', type='json')).json()
    weather_type = weather['dataseries'][0]['weather']
    weather_type = weather_lookup[weather_type]
    wind = weather['dataseries'][0]['wind10m']['direction'] + " " + str(weather['dataseries'][0]['wind10m']['speed']) + " mph"
    
    weather_list.append(weather_type + " " + wind)

game_DF["Weather"] = weather_list