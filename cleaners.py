import csv
import math

def clean_players(filename):
    """ Creates a file with only important data columns for each player

    Args:
        filename (str): Name of the file that contains the full data for each player
    """
    headers = ['first_name', 'second_name', 'goals_scored', 'assists', 'total_points', 'minutes', 'goals_conceded', 'creativity', 'influence', 'threat', 'bonus', 'bps', 'ict_index', 'clean_sheets', 'red_cards', 'yellow_cards', 'selected_by_percent', 'now_cost']
    fin = open(filename, 'r+', encoding='utf-8')
    fout = open('data/cleaned_players.csv', 'w+', encoding='utf-8', newline='')
    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, headers, extrasaction='ignore')
    writer.writeheader()
    for line in reader:
        writer.writerow(line)

def id_players(players_filename):
    """ Creates a file that contains the name to id mappings for each player

    Args:
        players_filename (str): Name of the file that contains the full data for each player
    """
    headers = ['first_name', 'second_name', 'id']
    fin = open(players_filename, 'r+', encoding='utf-8')
    fout = open('data/player_idlist.csv', 'w+', encoding='utf-8', newline='')
    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, headers, extrasaction='ignore')
    writer.writeheader()
    for line in reader:
        writer.writerow(line)

clean_players('data/players_raw.csv')
id_players('data/players_raw.csv')
