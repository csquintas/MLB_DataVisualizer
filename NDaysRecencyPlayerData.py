from datetime import date as dt
from datetime import datetime, timedelta
import statsapi
from teamInfo import team_id_lookup

def NDaysRecencyPlayerData(Game_DF, N_DAYS_AGO):
        
    teams_today = {}

    start, end = get_time_range(N_DAYS_AGO)

    PlayerStats_DF_List = {}

    for n in range(len(Game_DF)):
        matchup = Game_DF.iloc[n]['Game']
        away_team = matchup.split(' @ ')[0]
        home_team = matchup.split(' @ ')[1]
        home_team = home_team.split(' Game')[0]
        if away_team not in teams_today:
            teams_today[away_team] = team_id_lookup[away_team]
        if home_team not in teams_today:
            teams_today[home_team] = team_id_lookup[home_team]

    num_team_today = len(teams_today)
    count = 0
    for team, team_id in teams_today.items():
        count += 1
        #teams_player_info = {'dates':[]}
        teams_player_info = {} 
        for x in [y for y in statsapi.schedule(team=team_id,start_date=start,end_date=end)]:
            try:
                boxscore = statsapi.boxscore_data(x['game_id'])
                game_date = x['game_date']
                #teams_player_info['dates'].append(game_date)
            except:
                continue

            if boxscore['teamInfo']['away']['id'] == team_id:
                IS_TEAM_FLAG = 'away'
            else:
                IS_TEAM_FLAG = 'home'
            
            team_boxscore = boxscore[IS_TEAM_FLAG]['players']


            for player_id, player in team_boxscore.items():
                
                try:
                    position = player['position']['abbreviation']
                except:
                    continue

                if position == 'P':
                    continue

                player_name = player['person']['fullName']
                player_hitting_stats = player['stats']['batting']
                player_season_stats = player['seasonStats']['batting']
                bat_avg_key = player_name + " (" + team.split(" ")[-1] + ")" + " - " + "AVG"
                slg_key = player_name + " (" + team.split(" ")[-1] + ")" + " - " + "SLG"
                hr_key = player_name + " (" + team.split(" ")[-1] + ")" + " - " + "HR"
                player_date_key = player_name + " (" + team.split(" ")[-1] + ")" + " - " + "Game Dates"

                if bat_avg_key not in teams_player_info:
                    teams_player_info[bat_avg_key] = []
                    teams_player_info[slg_key] = []
                    teams_player_info[hr_key] = []
                    teams_player_info[player_date_key] = []

                try:
                    player_ba = player_season_stats['avg']
                except:
                    player_ba = '-'

                try:
                    player_hr = player_hitting_stats['homeRuns']
                except:
                    player_hr = 0
                    
                try:
                    player_slg = player_season_stats['slg']
                except:
                    player_slg = '-'


                teams_player_info[bat_avg_key].append(player_ba)
                teams_player_info[slg_key].append(player_slg) 
                teams_player_info[hr_key].append(player_hr)
                teams_player_info[player_date_key].append(game_date)
        
        PlayerStats_DF_List[team] = teams_player_info
        print(f"Completed {team}... Processed {count} of {num_team_today}")        
    return PlayerStats_DF_List

def get_time_range(N_DAYS_AGO):

    today = datetime.now()    
    n_days_ago = today - timedelta(days=N_DAYS_AGO)
    end = today.strftime("%m/%d/%Y")
    start = n_days_ago.strftime("%m/%d/%Y")

    return(start,end)
        