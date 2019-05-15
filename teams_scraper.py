from getters import *
from parsers import *
import sys
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: python teams_scraper.py <team_id>. Eg: python teams_scraper.py 5000")
        sys.exit(1)
    season = "18_19"
    output_folder = "team_" + sys.argv[1] + "_data" + season
    team_id = int(sys.argv[1])
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    summary = get_entry_data(team_id)
    # The link does not seem to be providing the right information
    gws = get_entry_gws_data(team_id)
    transfers = get_entry_transfers_data(team_id)
    parse_entry_history(summary, output_folder)
    parse_transfer_history(transfers, output_folder)
    parse_gw_entry_history(gws, output_folder)

if __name__ == '__main__':
    main()
