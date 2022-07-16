import requests
import json
from bs4 import BeautifulSoup
import re
import codecs
import pandas as pd
import os
import csv

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
    scripts = get_data("https://understat.com/league/EPL/2022")
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
            if data == 'var matchesData':
                content = re.findall(r'JSON\.parse\(\'(.*)\'\)',split_data[1])
                decoded_content = codecs.escape_decode(content[0], "hex")[0].decode('utf-8')
                matchesData = json.loads(decoded_content)
            elif data == 'var shotsData':
                content = re.findall(r'JSON\.parse\(\'(.*)\'\)',split_data[1])
                decoded_content = codecs.escape_decode(content[0], "hex")[0].decode('utf-8')
                shotsData = json.loads(decoded_content)
            elif data == 'var groupsData':
                content = re.findall(r'JSON\.parse\(\'(.*)\'\)',split_data[1])
                decoded_content = codecs.escape_decode(content[0], "hex")[0].decode('utf-8')
                groupsData = json.loads(decoded_content)
    return matchesData, shotsData, groupsData

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
    for d in playerData:
        matches, shots, groups = get_player_data(int(d['id']))
        indi_player_frame = pd.DataFrame.from_records(matches)
        player_name = d['player_name']
        player_name = player_name.replace(' ', '_')
        indi_player_frame.to_csv(os.path.join(outfile_base, player_name + '_' + d['id'] + '.csv'), index=False)

class PlayerID:
    def __init__(self, us_id, fpl_id, us_name, fpl_name):
        self.us_id = str(us_id)
        self.fpl_id = str(fpl_id)
        self.us_name = us_name
        self.fpl_name = fpl_name
        

def match_ids(understat_dir, data_dir):
    with open(os.path.join(understat_dir, 'understat_player.csv')) as understat_file:
        understat_inf = csv.DictReader(understat_file)
        ustat_players = {}
        for row in understat_inf:
            ustat_players[row['player_name']] = row['id']

    with open(os.path.join(data_dir, 'player_idlist.csv')) as fpl_file:
        fpl_players = {}
        fpl_inf = csv.DictReader(fpl_file)
        for row in fpl_inf:
            fpl_players[row['first_name'] + ' ' + row['second_name']] = row['id']
    players = []
    found = {}
    for k, v in ustat_players.items():
        if k in fpl_players:
            player = PlayerID(v, fpl_players[k], k, k)
            players += [player]
            found[k] = True
        else:
            player = PlayerID(v, -1, k, "")
            players += [player]

    for k, v in fpl_players.items():
        if k not in found:
            player = PlayerID(-1, v, "", k)
            players += [player]

    with open(os.path.join(data_dir, 'id_dict.csv'), 'w+') as outf:
        outf.write('Understat_ID, FPL_ID, Understat_Name, FPL_Name\n')
        for p in players:
            outf.write(p.us_id + "," + p.fpl_id + "," + p.us_name + "," + p.fpl_name + "\n")

def main():
    #parse_epl_data('data/2021-22/understat')
    #md, sd, gd = get_player_data(318)
    #match_frame = pd.DataFrame.from_records(md)
    #match_frame.to_csv('auba.csv', index=False)
    match_ids('data/2021-22/understat', 'data/2022-23')

if __name__ == '__main__':
    main()
