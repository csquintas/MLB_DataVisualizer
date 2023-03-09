from urllib.request import urlopen, Request
from SQLconfig import config #SQL DB info
from teamInfo import team_id_lookup
import mysql.connector
import ast
import pandas as pd
import re

def PitcherVsTeam(df):
    
    DF_list = []
    DF_list_unstyled = []

    cnx = mysql.connector.connect(**config)    
    cursor = cnx.cursor()
    num_games = len(df.index)
    #url ="https://baseballsavant.mlb.com/player_matchup?type=batter&teamPitching=119&teamBatting=112&player_id=664062"
    url = "https://baseballsavant.mlb.com/player_matchup?type=batter&teamPitching={Pitching_Team_ID}&teamBatting={Batting_Team_ID}&player_id={Pitcher_ID}"

    for n in range(num_games):
        print(f"Processing {n+1} of {num_games-1}...")
        game = df.iloc[n]

        matchup = game['Game']
        
        # Double Header Breaks it
        if "Game" in matchup:
            home_team = matchup.split(' @ ')[1][:-7]
        else:
            home_team = matchup.split(' @ ')[1]
            
        away_team = matchup.split(' @ ')[0]
        Home_ID = team_id_lookup[home_team]
        Away_ID = team_id_lookup[away_team]
        home_pitcher = game['Home Pitcher']
        away_pitcher = game['Away Pitcher']

        HOME_flag = 0
        AWAY_flag = 0

        if home_pitcher != "":
            home_pitcher_data = []
            HOME_flag = 1
            query = f"SELECT * FROM playerdetailsmap WHERE MLBNAME LIKE '{home_pitcher}'"
            with cnx.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                for home_pitcher_data in result:
                    continue
            
        if away_pitcher != "":
            away_pitcher_data = []
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
            home_Team_DF, home_Team_DF_unstyled = team_DF_generator(home_PvsB, home_pitcher_name, home_team, away_team, "AWAY")
            DF_list.append(home_Team_DF)
            DF_list_unstyled.append(home_Team_DF_unstyled)


        if AWAY_flag and len(away_pitcher_data) > 1:
            away_pitcher_name = away_pitcher_data[1]
            away_PvsB = html_parser(away_pitcher_data, Home_ID, Away_ID, "AWAY")
            away_Team_DF, away_Team_DF_unstyled = team_DF_generator(away_PvsB, away_pitcher_name, home_team, away_team, "HOME")
            DF_list.append(away_Team_DF)
            DF_list_unstyled.append(away_Team_DF_unstyled)

        print(f"Completed {n+1}...")

    return DF_list, DF_list_unstyled


def html_parser(pitcher_data, Home_ID, Away_ID, pitcher_team):

        pitcher_ID = pitcher_data[2]

        url = "https://baseballsavant.mlb.com/player_matchup?type=batter&teamPitching={Pitching_Team_ID}&teamBatting={Batting_Team_ID}&player_id={Pitcher_ID}"

        if pitcher_team == "HOME":
            pitcher_search = url.format(Pitching_Team_ID = Home_ID, Batting_Team_ID = Away_ID, Pitcher_ID = pitcher_ID) 
        elif pitcher_team == "AWAY":
            pitcher_search = url.format(Pitching_Team_ID = Away_ID, Batting_Team_ID = Home_ID, Pitcher_ID = pitcher_ID) 
        else:
            print("html_parser must be called with 'HOME' or 'AWAY' flags")
     
        # act as a browser
        try:
            page = urlopen(pitcher_search)
            html = page.read().decode("utf-8")
        except:
            req = Request(
                        url=pitcher_search, 
                        headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req).read().decode("utf-8")

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
            bb.append(player_data['bb'])

            kpercent.append(round(0 if player_data['k_percent'] is None else player_data['k_percent'],1))
            whiffpercent.append(round(0 if player_data['swing_miss_percent'] is None else player_data['swing_miss_percent'],1))
            ba.append(round(0 if player_data['ba'] is None else player_data['ba'],3))
            slg.append(round(0 if player_data['slg'] is None else player_data['slg'],3))
            xba.append(round(0 if player_data['xba'] is None else player_data['xba'],3))
            xslg.append(round(0 if player_data['xslg'] is None else player_data['xslg'],3))

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
        
        Team_DF_unstyled = Team_DF.copy()
        Team_DF = Team_DF.style.set_caption(caption)

        return Team_DF, Team_DF_unstyled
