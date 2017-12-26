import requests
import json
from utility import uprint
from parsers import *
from cleaners import *
import time

def get_data():
    """ Retrieve the fpl player data from the hard-coded url
    """
    response = requests.get("https://fantasy.premierleague.com/drf/bootstrap-static")
    if response.status_code != 200:
        raise Exception("Response was code " + str(response.status_code))
    responseStr = response.text
    data = json.loads(responseStr)
    return data

def get_individual_player_data(player_id):
    """ Retrieve the player-specific detailed data

    Args:
        player_id (int): ID of the player whose data is to be retrieved
    """
    base_url = "https://fantasy.premierleague.com/drf/element-summary/"
    full_url = base_url + str(player_id)
    response = ''
    while response == '':
        try:
            response = requests.get(full_url)
        except:
            time.sleep(5)
    if response.status_code != 200:
        raise Exception("Response was code " + str(response.status_code))
    data = json.loads(response.text)
    return data

def parse_data():
    """ Parse and store all the data
    """
    print("Getting data")
    data = get_data()
    season = '2017-18'
    base_filename = 'data/' + season + '/'
    print("Parsing summary data")
    parse_players(data["elements"], base_filename)
    print("Cleaning summay data")
    clean_players(base_filename + 'players_raw.csv', base_filename)
    print("Extracting player ids")
    id_players(base_filename + 'players_raw.csv', base_filename)
    player_ids = get_player_ids(base_filename)
    # TODO: parse other stats that may be useful
    num_players = len(data["elements"])
    player_base_filename = base_filename + 'players/'
    print("Extracting player specific data")
    for i in range(num_players):
        player_data = get_individual_player_data(i+1)
        parse_player_history(player_data["history_past"], player_base_filename, player_ids[i+1])
        parse_player_gw_history(player_data["history"], player_base_filename, player_ids[i+1])

def main():
    parse_data()

if __name__ == "__main__":
    main()
