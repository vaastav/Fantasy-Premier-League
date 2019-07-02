from parsers import *
from cleaners import *
from getters import *
from collector import collect_gw, merge_gw

def parse_data():
    """ Parse and store all the data
    """
    print("Getting data")
    data = get_data()
    season = '2019-20'
    base_filename = 'data/' + season + '/'
    print("Parsing summary data")
    parse_players(data["elements"], base_filename)
    try:
        gw_num = data["current-event"]
    except:
        gw_num = 0
        print("Season hasn't started yet m8")
    print("Cleaning summary data")
    clean_players(base_filename + 'players_raw.csv', base_filename)
    print("Extracting player ids")
    id_players(base_filename + 'players_raw.csv', base_filename)
    player_ids = get_player_ids(base_filename)
    # TODO: parse other stats that may be useful
    num_players = len(data["elements"])
    player_base_filename = base_filename + 'players/'
    gw_base_filename = base_filename + 'gws/'
    print("Extracting player specific data")
    for i in range(num_players):
        player_data = get_individual_player_data(i+1)
        parse_player_history(player_data["history_past"], player_base_filename, player_ids[i+1], i+1)
        parse_player_gw_history(player_data["history"], player_base_filename, player_ids[i+1], i+1)
    if gw_num > 0:
        print("Collecting gw scores")
        collect_gw(gw_num, player_base_filename, gw_base_filename) 
        print("Merging gw scores")
        merge_gw(gw_num, gw_base_filename)

def main():
    parse_data()

if __name__ == "__main__":
    main()
