import requests
import json
import csv
import pandas as pd

from constant import OVERALL_LEAGUE_ID, GAMEWEEKS, SEASON

from pathlib import Path

# adds the top 10 team ID's to this array
teamIDarray = []

# number of top manager information required.
topManagerNumber = 10

url = (
    "https://fantasy.premierleague.com/api/leagues-classic/"
    + str(OVERALL_LEAGUE_ID)
    + "/standings/"
)

response = requests.get(url)
data = response.text
parsed = json.loads(data)
managerParsed = parsed["standings"]["results"]

# open 3 files for writing
Path(f"data/{SEASON}/managers/").mkdir(parents=True, exist_ok=True)

manager_data = open(
    f"data/{SEASON}/managers/top_managers.csv", "w", newline="", encoding="utf-8"
)
gw_data = open(
    f"data/{SEASON}/managers/top_managers_gwInfo.csv", "w", newline="", encoding="utf-8"
)
gw_picks = open(
    f"data/{SEASON}/managers/top_managers_gwPicks.csv",
    "w",
    newline="",
    encoding="utf-8",
)

# create the 3 csv writer objects
csvwriter1 = csv.writer(manager_data)
csvwriter2 = csv.writer(gw_data)
csvwriter3 = csv.writer(gw_picks)

# get csv of top 10 manager information and write to top_managers.csv
count = 0
for manager in managerParsed:
    if count == 0:
        header = ["rank", "entry", "player_name", "entry_name", "total"]
        csvwriter1.writerow(header)
        count += 1

    if count <= topManagerNumber:
        csvwriter1.writerow(
            [
                manager["rank"],
                manager["entry"],
                manager["player_name"],
                manager["entry_name"],
                manager["total"],
            ]
        )

        count += 1
        teamIDarray.append(manager["entry"])

# for each teamID in the top 10, call the api and update both top_managers_gwInfo.csv
# and top_managers_gwPicks.csv
count1 = 0
count2 = 0
for teamID in teamIDarray:
    for x in GAMEWEEKS:
        url = (
            "https://fantasy.premierleague.com/api/entry/"
            + str(teamID)
            + "/event/"
            + str(x)
            + "/picks/"
        )
        response = requests.get(url)
        data = response.text
        parsed = json.loads(data)

        # write data to top_managers_gwInfo.csv
        if count1 == 0:
            header = [
                "team_id",
                "gw",
                "points",
                "bench",
                "gw_rank",
                "transfers",
                "hits",
                "total_points",
                "overall_ank",
                "team_value",
                "chip",
            ]

            csvwriter2.writerow(header)
            count1 += 1
        try:
            csvwriter2.writerow(
                [
                    teamID,
                    x,
                    parsed["entry_history"]["points"],
                    parsed["entry_history"]["points_on_bench"],
                    parsed["entry_history"]["rank"],
                    parsed["entry_history"]["event_transfers"],
                    parsed["entry_history"]["event_transfers_cost"],
                    parsed["entry_history"]["total_points"],
                    parsed["entry_history"]["overall_rank"],
                    int(parsed["entry_history"]["value"]) / 10,
                    parsed["active_chip"],
                ]
            )
        except Exception:
            continue

        # write data to top_managers_gwPicks.csv
        for i in range(len(parsed["picks"])):
            if count2 == 0:
                header = ["team_id", "gw", "id", "position", "multiplier"]
                csvwriter3.writerow(header)
                count2 += 1
            csvwriter3.writerow(
                [
                    teamID,
                    x,
                    parsed["picks"][i]["element"],
                    parsed["picks"][i]["position"],
                    parsed["picks"][i]["multiplier"],
                ]
            )

manager_data.close()
gw_data.close()
gw_picks.close()

# do some formatting on top_managers_gwPicks
# by adding the name of the player picked from player_idlist.csv
df = pd.read_csv(f"data/{SEASON}/managers/top_managers_gwPicks.csv")
df1 = pd.read_csv(f"data/{SEASON}/player_idlist.csv")

merged = df.merge(df1, on=["id"])
merged.drop("first_name", axis=1, inplace=True)
merged = merged[["team_id", "gw", "second_name", "id", "position", "multiplier"]]
merged.rename({"id": "player_id"}, axis=1, inplace=True)
merged = merged.sort_values(by=["team_id", "gw", "position"])
merged.to_csv(f"data/{SEASON}/managers/top_managers_gwPicks.csv", index=False)
