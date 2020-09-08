import csv
import math
import os

def clean_players(filename, base_filename):
    """ Creates a file with only important data columns for each player

    Args:
        filename (str): Name of the file that contains the full data for each player
    """
    headers = ['first_name', 'second_name', 'goals_scored', 'assists', 'total_points', 'minutes', 'goals_conceded', 'creativity', 'influence', 'threat', 'bonus', 'bps', 'ict_index', 'clean_sheets', 'red_cards', 'yellow_cards', 'selected_by_percent', 'now_cost', 'element_type']
    fin = open(filename, 'r+', encoding='utf-8')
    outname = base_filename + 'cleaned_players.csv'
    os.makedirs(os.path.dirname(outname), exist_ok=True)
    fout = open(outname, 'w+', encoding='utf-8', newline='')
    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, headers, extrasaction='ignore')
    writer.writeheader()
    for line in reader:
        if line['element_type'] == '1':
            line['element_type'] = 'GK'
        elif line['element_type'] == '2':
            line['element_type'] = 'DEF'
        elif line['element_type'] == '3':
            line['element_type'] = 'MID'
        elif line['element_type'] == '4':
            line['element_type'] = 'FWD'
        else:
            print("Oh boy")
        writer.writerow(line)

def id_players(players_filename, base_filename):
    """ Creates a file that contains the name to id mappings for each player

    Args:
        players_filename (str): Name of the file that contains the full data for each player
    """
    headers = ['first_name', 'second_name', 'id']
    fin = open(players_filename, 'r+', encoding='utf-8')
    outname = base_filename + 'player_idlist.csv'
    os.makedirs(os.path.dirname(outname), exist_ok=True)
    fout = open(outname, 'w+', encoding='utf-8', newline='')
    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, headers, extrasaction='ignore')
    writer.writeheader()
    for line in reader:
        writer.writerow(line)

def get_player_ids(base_filename):
    """ Gets the list of all player ids and player names
    """
    filename = base_filename + 'player_idlist.csv'
    fin = open(filename, 'r+', encoding='utf-8')
    reader = csv.DictReader(fin)
    player_ids = {}
    for line in reader:
        k = int(line['id'])
        v = line['first_name'] + '_' + line['second_name']
        player_ids[k] = v
    return player_ids
