import csv 
import os
from utility import uprint
import pandas as pd

def extract_stat_names(dict_of_stats):
    """ Extracts all the names of the statistics

    Args:
        dict_of_stats (dict): Dictionary containing key-alue pair of stats
    """
    stat_names = []
    for key, val in dict_of_stats.items():
        stat_names += [key]
    return stat_names

def parse_top_players(data, base_filename):
    rows = []
    for event in data['events']:
        gw = event['id']
        player_id = event['top_element']
        points = event['top_element_info']['points']
        row = {}
        row['gw'] = gw
        row['player_id'] = player_id
        row['points'] = points
        rows += [row]
    f = open(os.path.join(base_filename, 'best_players.csv'), 'w+', newline='')
    w = csv.DictWriter(f, ['gw', 'player_id', 'points'])
    w.writeheader()
    for row in rows:
        w.writerow(row)

def parse_players(list_of_players, base_filename):
    stat_names = extract_stat_names(list_of_players[0])
    filename = base_filename + 'players_raw.csv'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    f = open(filename, 'w+', encoding='utf8', newline='')
    w = csv.DictWriter(f, sorted(stat_names))
    w.writeheader()
    for player in list_of_players:
            w.writerow({k:str(v).encode('utf-8').decode('utf-8') for k, v in player.items()})

def parse_player_history(list_of_histories, base_filename, player_name, Id):
    if len(list_of_histories) > 0:
        stat_names = extract_stat_names(list_of_histories[0])
        filename = base_filename + player_name + '_' + str(Id) + '/history.csv'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        f = open(filename, 'w+', encoding='utf8', newline='')
        w = csv.DictWriter(f, sorted(stat_names))
        w.writeheader()
        for history in list_of_histories:
            w.writerow(history)

def parse_player_gw_history(list_of_gw, base_filename, player_name, Id):
    if len(list_of_gw) > 0:
        stat_names = extract_stat_names(list_of_gw[0])
        filename = base_filename + player_name + '_' + str(Id) + '/gw.csv'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        f = open(filename, 'w+', encoding='utf8', newline='')
        w = csv.DictWriter(f, sorted(stat_names))
        w.writeheader()
        for gw in list_of_gw:
            w.writerow(gw)

def parse_gw_entry_history(data, outfile_base):
    for gw in data:
        picks = gw['picks']
        event = gw['entry_history']['event']
        filename = "picks_" +str(event) + ".csv"
        picks_df = pd.DataFrame.from_records(picks)
        picks_df.to_csv(os.path.join(outfile_base, filename), index=False)

def parse_entry_history(data, outfile_base):
    chips_df = pd.DataFrame.from_records(data["chips"])
    chips_df.to_csv(os.path.join(outfile_base, 'chips.csv'))
    season_df = pd.DataFrame.from_records(data["past"])
    season_df.to_csv(os.path.join(outfile_base, 'history.csv'))
    #profile_data = data["entry"].pop('kit', data["entry"])
    #profile_df = pd.DataFrame.from_records(profile_data)
    #profile_df.to_csv(os.path.join(outfile_base, 'profile.csv'))
    gw_history_df = pd.DataFrame.from_records(data["current"])
    gw_history_df.to_csv(os.path.join(outfile_base, 'gws.csv'), index=False)

def parse_entry_leagues(data, outfile_base):
    classic_leagues_df = pd.DataFrame.from_records(data["leagues"]["classic"])
    classic_leagues_df.to_csv(os.path.join(outfile_base, 'classic_leagues.csv'))
    try:
        cup_leagues_df = pd.DataFrame.from_records(data["leagues"]["cup"]["matches"])
        cup_leagues_df.to_csv(os.path.join(outfile_base, 'cup_leagues.csv'))
    except KeyError:
        print("No cups yet")
    h2h_leagues_df = pd.DataFrame.from_records(data["leagues"]["h2h"])
    h2h_leagues_df.to_csv(os.path.join(outfile_base, 'h2h_leagues.csv'))

def parse_transfer_history(data, outfile_base):
    wildcards_df = pd.DataFrame.from_records(data)
    wildcards_df.to_csv(os.path.join(outfile_base, 'transfers.csv'), index=False)

def parse_fixtures(data, outfile_base):
    fixtures_df = pd.DataFrame.from_records(data)
    fixtures_df.to_csv(os.path.join(outfile_base, 'fixtures.csv'), index=False)

def parse_team_data(data, outfile_base):
    teams_df = pd.DataFrame.from_records(data)
    teams_df.to_csv(os.path.join(outfile_base, 'teams.csv'), index=False)
