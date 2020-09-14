import requests
import json
from bs4 import BeautifulSoup
import re
import codecs
import pandas as pd
import os

def get_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Response was code " + str(response.status_code))
    html = response.text
    parsed_html = BeautifulSoup(html, 'html.parser')
    scripts = parsed_html.findAll('script')
    filtered_scripts = []
    for script in scripts:
        if len(script.contents) > 0:
            filtered_scripts += [script]
    return scripts

def get_epl_data():
    scripts = get_data("https://understat.com/league/EPL/2020")
    teamData = {}
    playerData = {}
    for script in scripts:
        for c in script.contents:
            split_data = c.split('=')
            data = split_data[0].strip()
            if data == 'var teamsData':
                content = re.findall(r'JSON\.parse\(\'(.*)\'\)',split_data[1])
                decoded_content = codecs.escape_decode(content[0], "hex")[0].decode('utf-8')
                teamData = json.loads(decoded_content)
            elif data == 'var playersData':
                content = re.findall(r'JSON\.parse\(\'(.*)\'\)',split_data[1])
                decoded_content = codecs.escape_decode(content[0], "hex")[0].decode('utf-8')
                playerData = json.loads(decoded_content)
    return teamData, playerData

def get_player_data(id):
    scripts = get_data("https://understat.com/player/" + str(id))
    groupsData = {}
    matchesData = {}
    shotsData = {}
    for script in scripts:
        for c in script.contents:
            split_data = c.split('=')
            data = split_data[0].strip()
            print(data)

def parse_epl_data(outfile_base):
    teamData,playerData = get_epl_data()
    new_team_data = []
    for t,v in teamData.items():
        new_team_data += [v]
    for data in new_team_data:
        team_frame = pd.DataFrame.from_records(data["history"])
        team = data["title"].replace(' ', '_')
        team_frame.to_csv(os.path.join(outfile_base, 'understat_' + team + '.csv'), index=False)
    player_frame = pd.DataFrame.from_records(playerData)
    player_frame.to_csv(os.path.join(outfile_base, 'understat_player.csv'), index=False)

def main():
    #parse_epl_data('data/2019-20/understat')
    get_player_data(318)

if __name__ == '__main__':
    main()
