import requests
import json


def get_recent_gameweek_id():
    """
    Get's the most recent gameweek's ID.
    """

    data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    data = json.loads(data.content)

    gameweeks = data['events']

    for gameweek in gameweeks:
        if gameweek['finished'] == False:
            gameweek_id = gameweek['id']
            return gameweek_id - 1


if __name__ == '__main__':
    print(get_recent_gameweek_id())
