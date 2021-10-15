from getters import *
from parsers import *
import sys
import os

def store_data(team_id, output_folder, start_gw):
    summary = get_entry_data(team_id)
    personal_data = get_entry_personal_data(team_id)
    num_gws = len(summary["current"])
    num_gws = start_gw + len(summary["current"]) - 1
    gws = get_entry_gws_data(team_id, num_gws, start_gw)
    transfers = get_entry_transfers_data(team_id)
    parse_entry_history(summary, output_folder)
    parse_entry_leagues(personal_data, output_folder)
    parse_transfer_history(transfers, output_folder)
    parse_gw_entry_history(gws, output_folder)

def main():
    if len(sys.argv) < 3:
        print("Usage: python teams_scraper.py <team_id> <season_short_code> <start_gw>. Eg: python teams_scraper.py 5000 21_22 1")
        sys.exit(1)

    team_id = int(sys.argv[1])
    season = sys.argv[2]

    if len(sys.argv) == 4:
        start_gw = int(sys.argv[3])
    else:
        start_gw = 1

    output_folder = "team_" + sys.argv[1] + "_data" + season
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    store_data(team_id, output_folder, start_gw)

if __name__ == '__main__':
    main()
