import os

import pandas as pd

def explore_dfs():
    '''
    =========================
    Data root directory
    =========================
    '''
    data_path = os.path.join(os.getcwd(),'data')
    
    # List of teams, throughout the seasons
    fpath = os.path.join(data_path, 'master_team_list.csv')
    df = pd.read_csv(fpath)
    
    # Every season, every club, every player, every GW
    # 'season_x, name, position, team_x, assists, bonus, bps, clean_sheets, creativity, element, fixture, goals_conceded, goals_scored, ict_index, influence, kickoff_time, minutes, opponent_team, opp_team_name, own_goals, penalties_missed, penalties_saved, red_cards, round, saves, selected, team_a_score, team_h_score, threat, total_points, transfers_balance, transfers_in, transfers_out, value, was_home, yellow_cards, GW'
    fpath = os.path.join(data_path, 'cleaned_merged_seasons.csv')
    df = pd.read_csv(fpath)
    
    '''
    =========================
    Data/season directory
    =========================
    '''
    season_year = '2021-22'
    season_path = os.path.join(data_path,season_year)
    
    # Overview of all players, all the basic stats of their performance
    # 'first_name, second_name, goals_scored, assists, total_points, minutes, goals_conceded, creativity, influence, threat, bonus, bps, ict_index, clean_sheets, red_cards, yellow_cards, selected_by_percent, now_cost, element_type'
    fpath = os.path.join(season_path, 'cleaned_players.csv')
    df = pd.read_csv(fpath)
    
    # Scores, team ids (joins required to make this work)
    # 'code, event, finished, finished_provisional, id, kickoff_time, minutes, provisional_start_time, started, team_a, team_a_score, team_h, team_h_score, stats, team_h_difficulty, team_a_difficulty, pulse_id'
    fpath = os.path.join(season_path, 'fixtures.csv')
    df = pd.read_csv(fpath)
    
    # A table which sits above the understat and the player table of sorts
    # 'Understat_ID, FPL_ID,  Understat_Name, FPL_Name'
    fpath = os.path.join(season_path, 'id_dict.csv')
    df = pd.read_csv(fpath)
    
    # Player table
    # 'first_name, second_name, id'
    fpath = os.path.join(season_path, 'player_idlist.csv')
    df = pd.read_csv(fpath)
    
    # A file with A LOT of data in it. Not 100% the use case for this.
    # Each player has a unique line in it. Is it useful? Something to figure out.
    # 'assists, bonus, bps, chance_of_playing_next_round, chance_of_playing_this_round, clean_sheets, code, corners_and_indirect_freekicks_order, corners_and_indirect_freekicks_text, cost_change_event, cost_change_event_fall, cost_change_start, cost_change_start_fall, creativity, creativity_rank, creativity_rank_type, direct_freekicks_order, direct_freekicks_text, dreamteam_count, element_type, ep_next, ep_this, event_points, first_name, form, goals_conceded, goals_scored, ict_index, ict_index_rank, ict_index_rank_type, id, in_dreamteam, influence, influence_rank, influence_rank_type, minutes, news, news_added, now_cost, own_goals, penalties_missed, penalties_order, penalties_saved, penalties_text, photo, points_per_game, red_cards, saves, second_name, selected_by_percent, special, squad_number, status, team, team_code, threat, threat_rank, threat_rank_type, total_points, transfers_in, transfers_in_event, transfers_out, transfers_out_event, value_form, value_season, web_name, yellow_cards'
    fpath = os.path.join(season_path, 'players_raw.csv')
    df = pd.read_csv(fpath)
    
    # Unique team rows containing various 'threat' levels at home vs away.
    # Some very interesting data in here and could be used to create a bespoke
    # FDR.
    # 'code, draw, form, id, loss, name, played, points, position, short_name, strength, team_division, unavailable, win, strength_overall_home, strength_overall_away, strength_attack_home, strength_attack_away, strength_defence_home, strength_defence_away, pulse_id'
    fpath = os.path.join(season_path, 'teams.csv')
    df = pd.read_csv(fpath)
    
    '''
    =========================
    GW directory
    =========================
    '''
    # Every single player in every single gameweek.
    # I would love the freedom to plot these headings against each other at will
    # I would also love, on mouseover, a time-series of these to be revealed
    # 'name, position, team, xP, assists, bonus, bps, clean_sheets, creativity, element, fixture, goals_conceded, goals_scored, ict_index, influence, kickoff_time, minutes, opponent_team, own_goals, penalties_missed, penalties_saved, red_cards, round, saves, selected, team_a_score, team_h_score, threat, total_points, transfers_balance, transfers_in, transfers_out, value, was_home, yellow_cards, GW'
    subfolder = 'gws'
    sub_path = os.path.join(season_path, subfolder)
    fpath = os.path.join(sub_path, 'merged_gw.csv')
    df = pd.read_csv(fpath)
    
    '''
    =========================
    Players sub-directory
    =========================
    '''
    # A lot of data, at gameweek level, for a player
    # 'assists, bonus, bps, clean_sheets, creativity, element, fixture, goals_conceded, goals_scored, ict_index, influence, kickoff_time, minutes, opponent_team, own_goals, penalties_missed, penalties_saved, red_cards, round, saves, selected, team_a_score, team_h_score, threat, total_points, transfers_balance, transfers_in, transfers_out, value, was_home, yellow_cards'
    # !!! This is going to need a join on every single file called gw.csv
    subfolder = 'players'
    player = 'Anthony_Martial_278'
    filename = 'gw.csv'
    fpath = os.path.join(season_path, subfolder, player, filename)
    df = pd.read_csv(fpath)
    
    '''
    =========================
    Understat sub-directory
    =========================
    '''
    # !!! Lots of player specific data. Will need a name column inserted w.r.t
    # the filename. There is no obvious player ID foreign key so using this will
    # be a little convoluted. This data stretches very far back for some players.
    # !!! This is going to need a loop and a pd.concat operation too.
    # 'goals, shots, xG, time, position, h_team, a_team, h_goals, a_goals, date, id, season, roster_id, xA, assists, key_passes, npg, npxG, xGChain, xGBuildup'
    subfolder = 'understat'
    player = 'Anthony_Martial_553.csv'
    fpath = os.path.join(season_path, subfolder, player)
    df = pd.read_csv(fpath)

    # There is a summary document which appears to have an aggregate of these
    # stats, with a unique line for each player. Could be very useful. Some
    # Massively useful by itself. No join exists though unless you do it on name
    fpath = os.path.join(season_path, subfolder, 'understat_player.csv')
    df = pd.read_csv(fpath)
    
    print('fini')

if __name__ == '__main__':
    explore_dfs()

__doc__ = '''
Set breakpoints up in the main function to see individual data sources / frames

This is just to highlight what bits of data is found where and what might need
to be done to join these data points together to create a coherent model.
'''