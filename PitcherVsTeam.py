import mysql.connector
from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import json
import ast
import pandas as pd
import re

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
    
    config = {
        'user': 'root',
        'password': 'Qdog176782',
        'host': '127.0.0.1',
        'port': '3306',
        'database': 'mlbPlayers',
        'raise_on_warnings': True,}
        
    result = []
    cnx = mysql.connector.connect(**config)    
    cursor = cnx.cursor()
    num_games = len(df.index)
    #url ="https://baseballsavant.mlb.com/player_matchup?type=batter&teamPitching=119&teamBatting=112&player_id=664062"
    url = "https://baseballsavant.mlb.com/player_matchup?type=batter&teamPitching={Pitching_Team_ID}&teamBatting={Batting_Team_ID}&player_id={Pitcher_ID}"

    for n in range(num_games):
        print(f"Processing {n}...")
        game = df.iloc[n]
        home_pitcher = game['Home Pitcher']
        away_pitcher = game['Away Pitcher']

        if home_pitcher == "" or away_pitcher == "":
            continue
        matchup = game['Game']
        home_team = matchup.split(' @ ')[1]
        away_team = matchup.split(' @ ')[0]
        Home_ID = team_id_lookup[home_team]
        Away_ID = team_id_lookup[away_team]


        query = f"SELECT * FROM playerdetailsmap WHERE MLBNAME LIKE '{home_pitcher}'"
        with cnx.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            for home_pitcher_data in result:
                continue

        query = f"SELECT * FROM playerdetailsmap WHERE MLBNAME LIKE '{home_pitcher}'"
        with cnx.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            for away_pitcher_data in result:
                continue   

        home_pitcher_ID = home_pitcher_data[2]
        away_pitcher_ID = away_pitcher_data[2]
    
        home_pitcher_search = url.format(Pitching_Team_ID = Home_ID, Batting_Team_ID = Away_ID, Pitcher_ID = home_pitcher_ID) 
        away_pitcher_search = url.format(Pitching_Team_ID = Away_ID, Batting_Team_ID = Home_ID, Pitcher_ID = away_pitcher_ID) 

        page = urlopen(home_pitcher_search)
        html = page.read().decode("utf-8")

        pattern ="var data =.*\\n"
        match_results = re.search(pattern,html, re.IGNORECASE)
        PvsB = match_results.group()
        PvsB = re.sub("var data =", "", PvsB) # Remove HTML tags
        PvsB = re.sub(";\n", "", PvsB) # Remove HTML tags
        PvsB = re.sub("null","None", PvsB) # Remove HTML tags
        PvsB = ast.literal_eval(PvsB)   

        team_hitting_data = PvsB['team']
        away_Team_DF = pd.DataFrame({})
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

        away_Team_DF["Player"] = player_list
        away_Team_DF["PA"] = pa
        away_Team_DF["AB"] = ab
        away_Team_DF["H"] = hits
        away_Team_DF["2B"] = dbls
        away_Team_DF["3B"] = triples
        away_Team_DF["HR"] = hr
        away_Team_DF["SO"] = so
        away_Team_DF["K%"] = kpercent
        away_Team_DF["Whiff%"] = whiffpercent
        away_Team_DF["BB%"] = bb
        away_Team_DF["BA"] = ba
        away_Team_DF["SLG"] = slg
        away_Team_DF["xBA"] = xba
        away_Team_DF["xSLG"] = xslg   

        caption = f"{away_team} Historical Batting Stats Against {home_pitcher}"
        away_Team_DF = away_Team_DF.style.set_caption(caption)

        page = urlopen(away_pitcher_search)
        html = page.read().decode("utf-8")

        pattern ="var data =.*\\n"
        match_results = re.search(pattern,html, re.IGNORECASE)
        PvsB = match_results.group()
        PvsB = re.sub("var data =", "", PvsB) # Remove HTML tags
        PvsB = re.sub(";\n", "", PvsB) # Remove HTML tags
        PvsB = re.sub("null","None", PvsB) # Remove HTML tags
        PvsB = ast.literal_eval(PvsB)   

        team_hitting_data = PvsB['team']
        home_Team_DF = pd.DataFrame({})
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

        home_Team_DF["Player"] = player_list
        home_Team_DF["PA"] = pa
        home_Team_DF["AB"] = ab
        home_Team_DF["H"] = hits
        home_Team_DF["2B"] = dbls
        home_Team_DF["3B"] = triples
        home_Team_DF["HR"] = hr
        home_Team_DF["SO"] = so
        home_Team_DF["K%"] = kpercent
        home_Team_DF["Whiff%"] = whiffpercent
        home_Team_DF["BB%"] = bb
        home_Team_DF["BA"] = ba
        home_Team_DF["SLG"] = slg
        home_Team_DF["xBA"] = xba
        home_Team_DF["xSLG"] = xslg   

        caption = f"{home_team} Historical Batting Stats Against {away_pitcher}"
        home_Team_DF = home_Team_DF.style.set_caption(caption)

        result.append(home_Team_DF)
        result.append(away_Team_DF)
        print(f"Completed {n}...")

    return result