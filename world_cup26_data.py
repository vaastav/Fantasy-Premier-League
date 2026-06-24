import json
import requests
import unidecode
import csv
import sys

class Player:
    def __init__(self, obj, squad) -> None:
        self.id = obj['id']
        self.name = unidecode.unidecode(obj['firstName']) + " " + unidecode.unidecode(obj['lastName'])
        self.squad = squad
        self.price = float(obj["price"])
        self.status = obj['status']
        self.position = obj['position']
        self.totalPoints = obj['stats']['totalPoints']
        self.avgPoints = obj['stats']['avgPoints']
        if isinstance(obj['stats']['roundPoints'], list):
            self.round0 = 0
            self.round1 = 0
            self.round2 = 0
            self.round3 = 0
            self.round4 = 0
            self.round5 = 0
            self.round6 = 0
            self.round7 = 0
            return
        self.round0 = obj['stats']['roundPoints'].get("1", 0)
        self.round1 = obj['stats']['roundPoints'].get("2", 0)
        self.round2 = obj['stats']['roundPoints'].get("3", 0)
        self.round3 = obj['stats']['roundPoints'].get("4", 0)
        self.round4 = obj['stats']['roundPoints'].get("5", 0)
        self.round5 = obj['stats']['roundPoints'].get("6", 0)
        self.round6 = obj['stats']['roundPoints'].get("7", 0)
        self.round7 = obj['stats']['roundPoints'].get("8", 0)


def get_data():
    """
    Retrieve the world cup fantasy data from the hard-coded url
    """
    response = requests.get("https://play.fifa.com/json/fantasy/players.json", headers={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0"})
    if response.status_code != 200:
        raise Exception("Response was code " + str(response.status_code))
    responseStr = response.text
    data = json.loads(responseStr)
    return data

def get_squads():
    """
    Retrieve the squad data from the hard-coded url
    """
    response = requests.get("https://play.fifa.com/json/fantasy/squads.json", headers={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0"})
    if response.status_code != 200:
        raise Exception("Response was code " + str(response.status_code))
    responseStr = response.text
    data = json.loads(responseStr)
    return data

def get_wc_data():
    player_data = get_data()
    squads = get_squads()
    squads_dict = {}
    for d in squads:
        squads_dict[d['id']] = d['abbr']
    players = []
    print(squads_dict)
    for d in player_data:
        squad_name = squads_dict[d['squadId']]
        player = Player(d, squad_name)
        players += [player]
    
    return players

def main():
    players = get_wc_data()
    fieldnames = vars(players[0]).keys()
    print("Writing csv file now")
    with open("data/world_cup_2026.csv", "w", newline="") as inf:
        writer = csv.DictWriter(inf, fieldnames=fieldnames)
        writer.writeheader()

        for obj in players:
            writer.writerow(vars(obj))
    print("Finished writing csv file")

if __name__ == '__main__':
    main()
