#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 22:06:52 2022

@author: christopherquintas
"""
from datetime import date as dt
from teamInfo import stadium_info, weather_lookup
import pandas as pd
import requests
import statsapi
import re

class GameDay:

    stadium_info = stadium_info    
    weather_lookup = weather_lookup
    
    def __init__(self):

        self.game_DF = pd.DataFrame({})
        self.games_list = []
        self.games_times = []
        self.location_list = []

    def GameDay_Wrapper(self, date = None):
        
        self.date = self.get_date(date)
        schedule = statsapi.schedule(self.date)
        self.doubleheaders = set()
        games_list = []
        games_times = []
        home_pitcher_list = []
        away_pitcher_list =[]
        location_list = []
        
        print(f"Getting List of Games on {self.date}")
        print("Matchups, Start Times, Probable Pitchers, and Weather will be added to a DataFrame")

        for game in schedule:
            
            home, away, matchup = self.get_teams(game)
            game_time = self.get_start_time(game)
            location = self.get_location(home)
            home_pitcher, away_pitcher = self.get_pitcher(game, home, away)
            
            if game['doubleheader'] == 'S':
                matchup = self.doubleheader_check(home, matchup)
            
            games_list.append(matchup)
            games_times.append(game_time)
            home_pitcher_list.append(home_pitcher)
            away_pitcher_list.append(away_pitcher)
            location_list.append(location)

        weather_list = self.get_weather(location_list)
        
        self.game_DF["Game"] = games_list
        self.game_DF["Time"] = games_times
        self.game_DF["Home Pitcher"] = home_pitcher_list
        self.game_DF["Away Pitcher"] = away_pitcher_list
        self.game_DF["Weather"] = weather_list
        print(f"DataFrame of Games on {self.date}:")
        return self.game_DF
    
   
    
    def get_weather(self, locations):   
        
        print("Fetching Weather Data: This may take up to 30 seconds")
        url = "http://www.7timer.info/bin/api.pl?lon={lon}&lat={lat}&product={product}&output={type}"      
        weather_list = []
        
        for location in locations:
            lon = location[0]
            lat = location[1]
            weather = requests.get(url.format(lon = lon, lat = lat, product='civil', type='json')).json()
            weather_type = weather['dataseries'][0]['weather']
            weather_type = self.weather_lookup[weather_type]
            wind = weather['dataseries'][0]['wind10m']['direction'] + " " + str(weather['dataseries'][0]['wind10m']['speed']) + " mph"

            weather_list.append(weather_type + " " + wind)
        return weather_list
            
    def get_pitcher(self, game, home, away):
        
        home_pitcher = game['home_probable_pitcher']
        away_pitcher = game['away_probable_pitcher']
        
        return home_pitcher, away_pitcher
    
    def doubleheader_check(self, home, matchup):
        
        if home not in self.doubleheaders:
            matchup = matchup + " Game 1"
            self.doubleheaders.add(matchup)
        else:
            matchup = matchup + " Game 2"
    
        return matchup
    
    def get_location(self, home):
        
        location_data = list(filter(lambda team: team['team'] == home, self.stadium_info))[0]
        location = [location_data['lng'], location_data['lat']]
        
        return location
    
    def get_date(self, date = None):
        
        #m/d/y
        
        if date == None:
            date = dt.today()
            date = date.strftime("%m/%d/%Y")
        
        return date
    
    def get_teams(self, game):
        
        home_team = game['home_name']
        away_team = game['away_name']
        matchup = away_team + " @ " + home_team 
        
        return home_team, away_team, matchup
    
    def get_start_time(self, game):
        
        game_time = game['game_datetime']
        game_time = re.findall('\d{2}:\d{2}', game_time)[0]
        hour = int(game_time[:2])
    
        #Time Change for when games start at [1,5] AM 
        if hour <= 5:
            hour = 24 + hour
            
        hour = hour - 7 #MST     
        mins = game_time[3:]
        if hour >= 12:
            std_time =  hour % 12
            if std_time == 0:
                std_time = 12
            game_time = str(std_time) + ':' + mins + " PM MST"
        else:
            game_time = str(hour) + ':' + mins + " AM MST"
            
        return game_time    
        