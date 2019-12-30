from datetime import datetime
import requests
import json


def get_recent_gameweek_id():
    """
    Get's the most recent gameweek's ID.
    """

    data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    data = json.loads(data.content)

    gameweeks = data['events']
    
    now = datetime.utcnow()
    for gameweek in gameweeks:
        next_deadline_date = datetime.strptime(gameweek['deadline_time'], '%Y-%m-%dT%H:%M:%SZ')
        if next_deadline_date > now:
            return gameweek['id'] - 1


if __name__ == '__main__':
    print(get_recent_gameweek_id())
