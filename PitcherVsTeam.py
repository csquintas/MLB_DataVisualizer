from turtle import home
import mysql.connector
from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import json
import ast
import pandas as pd
import re
from config import * #SQL DB info

def PitcherVsTeam(df):

    team_id_lookup =  {
                "Los Angeles Angels":108,
                "Arizona Diamondbacks":109,
                "Atlanta Braves":144,
                "Baltimore Orioles":110,
                "Boston Red Sox":111,
                "Chicago Cubs":112,
                "Chicago White Sox":145,
                "Cincinnati Reds":113,
                "Cleveland Guardians":114,
                "Colorado Rockies":115,
                "Detroit Tigers":116,
                "Miami Marlins":146,
                "Houston Astros":117,
                "Kansas City Royals":118,
                "Los Angeles Dodgers":119,
                "Milwaukee Brewers":158,
                "Minnesota Twins":142,
                "New York Mets":121,
                "New York Yankees":147,
                "Oakland Athletics":133,
                "Philadelphia Phillies":143,
                "Pittsburgh Pirates":134,
                "St. Louis Cardinals":138,
                "San Diego Padres":135,
                "San Francisco Giants":137,
                "Seattle Mariners":136,
                "Tampa Bay Rays":139,
                "Texas Rangers":140,
                "Toronto Blue Jays":141,
                "Washington Nationals":120,
            }  
    
    config = config 

    DF_list = []
    cnx = mysql.connector.connect(**config)    
    cursor = cnx.cursor()
    num_games = len(df.index)
    #url ="https://baseballsavant.mlb.com/player_matchup?type=batter&teamPitching=119&teamBatting=112&player_id=664062"
    url = "https://baseballsavant.mlb.com/player_matchup?type=batter&teamPitching={Pitching_Team_ID}&teamBatting={Batting_Team_ID}&player_id={Pitcher_ID}"

    for n in range(num_games):
        print(f"Processing {n}...")
        game = df.iloc[n]

        matchup = game['Game']
        home_team = matchup.split(' @ ')[1]
        away_team = matchup.split(' @ ')[0]
        Home_ID = team_id_lookup[home_team]
        Away_ID = team_id_lookup[away_team]
        home_pitcher = game['Home Pitcher']
        away_pitcher = game['Away Pitcher']

        HOME_flag = 0
        AWAY_flag = 0

        if home_pitcher != "":
            HOME_flag = 1
            query = f"SELECT * FROM playerdetailsmap WHERE MLBNAME LIKE '{home_pitcher}'"
            with cnx.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                for home_pitcher_data in result:
                    continue
            
        if away_pitcher != "":
            AWAY_flag = 1
            query = f"SELECT * FROM playerdetailsmap WHERE MLBNAME LIKE '{away_pitcher}'"
            with cnx.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                for away_pitcher_data in result:
                    continue   



        if HOME_flag and len(home_pitcher_data) > 1:
            home_pitcher_name = home_pitcher_data[1]
            home_PvsB = html_parser(home_pitcher_data, Home_ID, Away_ID, "HOME")
            home_Team_DF = team_DF_generator(home_PvsB, home_pitcher_name, home_team, away_team, "AWAY")
            DF_list.append(home_Team_DF)

        if AWAY_flag and len(away_pitcher_data) > 1:
            away_pitcher_name = away_pitcher_data[1]
            away_PvsB = html_parser(away_pitcher_data, Home_ID, Away_ID, "AWAY")
            away_Team_DF = team_DF_generator(away_PvsB, away_pitcher_name, home_team, away_team, "HOME")
            DF_list.append(away_Team_DF)

        print(f"Completed {n}...")

    return DF_list


def html_parser(pitcher_data, Home_ID, Away_ID, pitcher_team):

        pitcher_ID = pitcher_data[2]

        url = "https://baseballsavant.mlb.com/player_matchup?type=batter&teamPitching={Pitching_Team_ID}&teamBatting={Batting_Team_ID}&player_id={Pitcher_ID}"

        if pitcher_team == "HOME":
            pitcher_search = url.format(Pitching_Team_ID = Home_ID, Batting_Team_ID = Away_ID, Pitcher_ID = pitcher_ID) 
        elif pitcher_team == "AWAY":
            pitcher_search = url.format(Pitching_Team_ID = Away_ID, Batting_Team_ID = Home_ID, Pitcher_ID = pitcher_ID) 
        else:
            print("html_parser must be called with 'HOME' or 'AWAY' flags")
     

        page = urlopen(pitcher_search)
        html = page.read().decode("utf-8")

        pattern ="var data =.*\\n"
        match_results = re.search(pattern,html, re.IGNORECASE)
        PvsB = match_results.group()
        PvsB = re.sub("var data =", "", PvsB) # Remove HTML tags
        PvsB = re.sub(";\n", "", PvsB) # Remove HTML tags
        PvsB = re.sub("null","None", PvsB) # Remove HTML tags
        PvsB = ast.literal_eval(PvsB)

        return PvsB   

def team_DF_generator(PvsB, pitcher, home_team, away_team, hitting_team):

        team_hitting_data = PvsB['team']
        Team_DF = pd.DataFrame({})
        player_list = []
        pa = []
        ab = []
        hits = []
        dbls = []
        triples = []
        hr = []
        so = []
        kpercent = []
        whiffpercent = []
        bb = []
        ba = []
        slg = []
        xba = []
        xslg = []


        for player_data in team_hitting_data:
            player_list.append(player_data['player_name'])
            pa.append(player_data['pa'])
            ab.append(player_data['abs'])
            hits.append(player_data['hits'])
            dbls.append(player_data['dbls'])
            triples.append(player_data['triples'])
            hr.append(player_data['hrs'])
            so.append(player_data['so'])
            kpercent.append(player_data['k_percent'])
            whiffpercent.append(player_data['swing_miss_percent'])
            bb.append(player_data['bb'])
            ba.append(player_data['ba'])
            slg.append(player_data['slg'])
            xba.append(player_data['xba'])
            xslg.append(player_data['xslg'])

        Team_DF["Player"] = player_list
        Team_DF["PA"] = pa
        Team_DF["AB"] = ab
        Team_DF["H"] = hits
        Team_DF["2B"] = dbls
        Team_DF["3B"] = triples
        Team_DF["HR"] = hr
        Team_DF["SO"] = so
        Team_DF["K%"] = kpercent
        Team_DF["Whiff%"] = whiffpercent
        Team_DF["BB%"] = bb
        Team_DF["BA"] = ba
        Team_DF["SLG"] = slg
        Team_DF["xBA"] = xba
        Team_DF["xSLG"] = xslg   

        if hitting_team == "HOME":
            caption = f"{home_team} Historical Batting Stats Against {pitcher}"
        elif hitting_team == "AWAY":
            caption = f"{away_team} Historical Batting Stats Against {pitcher}"

        Team_DF = Team_DF.style.set_caption(caption)

        return Team_DF
