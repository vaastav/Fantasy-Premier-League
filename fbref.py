import requests
from bs4 import BeautifulSoup
from bs4 import Comment
import time
import csv

class MatchData:
    def __init__(self) -> None:
        self.comp = ""
        self.date = ""
        self.round = ""
        self.data = {}


class PlayerData:
    def __init__(self) -> None:
        self.data = {}
        self.base_url = ""
        self.matches_links = []

def get_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Response was code " + str(response.status_code))
    html = response.text
    parsed_html =  BeautifulSoup(html, 'html.parser')
    comments = parsed_html.find_all(string=lambda text: isinstance(text, Comment))
    tables = []
    for c in comments:
        if '<table' in c:
            table_html = BeautifulSoup(c, 'html.parser')
            tables = table_html.find_all('table')
    return tables

def get_table_data(url):
    status_code = 0
    while status_code != 200:
        print("Getting data for: " + url)
        response = requests.get(url)
        status_code = response.status_code
        if status_code != 200:
            time.sleep(5)
    html = response.text
    parsed_html = BeautifulSoup(html, 'html.parser')
    tables = parsed_html.find_all('table')
    return tables[0]

def get_matches_data(player):
    tables = []
    for l in player.matches_links:
        tables += [get_table_data(l)]
    matches = []
    for t in tables:
        for row in t.tbody.find_all('tr'):
            data = {}
            class_name = row.get('class')
            if class_name != None and len(class_name) > 0:
                continue
            columns = row.find_all('td') + row.find_all('th')
            for c in columns:
                data_stat = c.get('data-stat')
                if data_stat in ['date', 'round', 'comp']:
                    a_html = BeautifulSoup(str(c.contents[0]), 'html.parser')
                    a = a_html.find_all('a')
                    data[data_stat] = a[0].contents[0]
                else:
                    if len(c.contents) == 0:
                        continue
                    data[data_stat] = c.contents[0]
            match = MatchData()
            match.date = data['date']
            match.round = data['round']
            match.comp = data['comp']
            del data['date']
            del data['round']
            del data['comp']
            matches += [match]
    player.matches = matches

def get_epl_players():
    tables = get_data("https://fbref.com/en/comps/9/stats/Premier-League-Stats")
    table = tables[0]
    players = {}
    stat_names = set()
    for row in table.tbody.find_all('tr'):
        columns = row.find_all('td')
        base_url = ""
        matches_link = ""
        player_id = ""
        stats = {}
        for c in columns:
            data_stat = c.get('data-stat')
            if data_stat == 'player':
                a_html = BeautifulSoup(str(c.contents[0]), 'html.parser')
                a = a_html.find_all('a')
                base_url = "https://fbref.com" + a[0].get('href')
                link = a[0].get('href')
                pieces = link.split('/')
                player_id = pieces[3]
                stats[data_stat] = a[0].contents[0]
                stat_names.add(data_stat)
            elif data_stat == 'squad':
                a_html = BeautifulSoup(str(c.contents[0]), 'html.parser')
                a = a_html.find_all('a')
                stats[data_stat] = a[0].contents[0]
                stat_names.add(data_stat)
            elif data_stat == "matches":
                a_html = BeautifulSoup(str(c.contents[0]), 'html.parser')
                a = a_html.find_all('a')
                matches_link = "https://fbref.com" + a[0].get('href')
            elif data_stat == "nationality":
                continue
            else:
                stats[data_stat] = c.contents[0]
                stat_names.add(data_stat)
        player = PlayerData()
        if player_id in players:
            player = players[player_id]
        player.base_url = base_url
        player.matches_links += [matches_link]
        player.data = stats
        players[player_id] = player
    return players, stat_names
            

def main():
    players, stats = get_epl_players()

    #for id, player in players.items():
    #    get_matches_data(player)

    with open('data/2021-22/fbref_overview.csv', 'w') as outf:
        writer = csv.DictWriter(outf, fieldnames=list(stats))
        writer.writeheader()
        for id, player in players.items():
            writer.writerow(player.data)

if __name__ == '__main__':
    main()