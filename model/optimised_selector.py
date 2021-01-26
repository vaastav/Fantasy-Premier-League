"""
    Having created a predictions csv, this script aims to select the optimal starting 11 given the FPL rule constraints.
    This is 0/1 Knapsack problem.
    A recursive dynamic programming function will be used. 

    General FPL constraints:
        Pick 15 players

        Constraints:
        - 100m budget
        - 3 FWD, 5 MID, 5 DEF, 2 GK
        - ≤3 players from same club

        Optimise for highest points total from:
        - 11/15 players
        - GK = 1, DEF ≥3, MID ≥3, FWD≥1
"""
import pandas as pd
import numpy as np
import os
import time
from typing import List
from pulp import *

PLAYERS = None
MATRIX = None

def importData()-> pd.DataFrame:
    """
        Read predictions data from csv into pandas DataFrame.
    """
    path = os.path.abspath(os.path.join(os.getcwd(), ''))
    df = pd.read_csv(path + '/_prediction.csv', index_col=0)
    return df

def subsetData(df, sortby, n):
    """
        Take the top n records according to column "sortby"
    """
    return df.sort_values(by = [sortby], ascending =False)[0:n]

def optimumTeam(budget, number_of_players=None, full_squad= True):

    data = importData()

    """
        In prediction script add other variables (red cards, injuries, greater than 0 starts?)
    """

    if number_of_players is not None:
        # take subset of total players
        data = subsetData(data, "y_pred", number_of_players)
    
    player = [str(i) for i in data.index]
    point = {str(i): data['y_pred'][i] for i in data.index} 
    cost = {str(i): data['value'][i] for i in data.index}
    gk = {str(i): 1 if data['element_type'][i] == 1 else 0 for i in data.index}
    defe = {str(i): 1 if data['element_type'][i] == 2 else 0 for i in data.index}
    mid = {str(i): 1 if data['element_type'][i] == 3 else 0 for i in data.index}
    stri = {str(i): 1 if data['element_type'][i] == 4 else 0 for i in data.index}
    teams = [0]
    for t in range(1, 21):
        team = {str(i): 1 if data['team'][i] == t else 0 for i in data.index}
        teams.append(team)
    stri = {str(i): 1 if data['element_type'][i] == 4 else 0 for i in data.index}

    # Maximize
    prob = LpProblem("FPL Problem", LpMaximize)
    player_vars = LpVariable.dicts("Players",player,0,1,LpBinary)

    # objective function
    prob += lpSum([point[i]*player_vars[i] for i in player]), "Total Points"

    # constraint
    if full_squad:
        prob += lpSum([player_vars[i] for i in player]) == 15, "Total 15 Players"
        prob += lpSum([gk[i] * player_vars[i] for i in player]) == 2, "2 GKs"
        prob += lpSum([defe[i] * player_vars[i] for i in player]) == 5, "5 DEF"
        prob += lpSum([mid[i] * player_vars[i] for i in player]) == 5, "5 MID"
        prob += lpSum([stri[i] * player_vars[i] for i in player]) == 3, "3 STR"

    else:
        prob += lpSum([player_vars[i] for i in player]) == 11, "Total 11 Players"
        prob += lpSum([gk[i] * player_vars[i] for i in player]) == 1, "Only 1 GK"
        prob += lpSum([defe[i] * player_vars[i] for i in player]) <= 5, "Less than 5 DEF"
        prob += lpSum([mid[i] * player_vars[i] for i in player]) <= 5, "Less than 5 MID"
        prob += lpSum([stri[i] * player_vars[i] for i in player]) <= 3, "Less than 3 STR"
        prob += lpSum([defe[i] * player_vars[i] for i in player]) >= 3, "At least 3 DEF"
        prob += lpSum([mid[i] * player_vars[i] for i in player]) >= 3, "At least 3 MID"
        prob += lpSum([stri[i] * player_vars[i] for i in player]) >= 1, "At least 1 STR"


    prob += lpSum([cost[i] * player_vars[i] for i in player]) <= budget, "Total Cost"
    for t in range(1,21):
        prob += lpSum([teams[t][str(i)] * player_vars[i] for i in player]) <= 3, "Less than 3 from team " + str(t)
   
    # solve
    status = prob.solve()
    print(LpStatus[status])
    
    player_indices = []
    for v in prob.variables():
        if v.varValue>0:
            player_indices.append(int(v.name[8:]))

    new_squad = data[data.index.isin(player_indices)].sort_values(["element_type"])
    print(new_squad)
    print("cost is ", new_squad["value"].sum())


def best_transfer(full_squad, squad, budget, transfers):

    data = importData()

    data["my_squad"] = np.where(data.index.isin(squad), 1, 0)
    my_squad_value = data.loc[data["my_squad"] == 1, "value"].sum()

    player = [str(i) for i in data.index]
    point = {str(i): data['y_pred'][i] for i in data.index} 
    cost = {str(i): data['value'][i] for i in data.index}
    gk = {str(i): 1 if data['element_type'][i] == 1 else 0 for i in data.index}
    defe = {str(i): 1 if data['element_type'][i] == 2 else 0 for i in data.index}
    mid = {str(i): 1 if data['element_type'][i] == 3 else 0 for i in data.index}
    stri = {str(i): 1 if data['element_type'][i] == 4 else 0 for i in data.index}

    # team index starts from 1 so a arbitrary value at 0 index is placed here.
    teams = [0]
    for t in range(1, 21):
        team = {str(i): 1 if data['team'][i] == t else 0 for i in data.index}
        teams.append(team)
    stri = {str(i): 1 if data['element_type'][i] == 4 else 0 for i in data.index}

    # extra metric
    current_squad = {str(i): 1 if data['my_squad'][i] == 1 else 0 for i in data.index}

    # Maximize
    prob = LpProblem("FPL Problem", LpMaximize)
    player_vars = LpVariable.dicts("Players",player,0,1,LpBinary)

    # objective function
    prob += lpSum([point[i]*player_vars[i] for i in player]), "Total Points"

    # constraint
    if full_squad:
        prob += lpSum([player_vars[i] for i in player]) == 15, "Total 15 Players"
        prob += lpSum([gk[i] * player_vars[i] for i in player]) == 2, "2 GKs"
        prob += lpSum([defe[i] * player_vars[i] for i in player]) == 5, "5 DEF"
        prob += lpSum([mid[i] * player_vars[i] for i in player]) == 5, "5 MID"
        prob += lpSum([stri[i] * player_vars[i] for i in player]) == 3, "3 STR"

    else:
        prob += lpSum([player_vars[i] for i in player]) == 11, "Total 11 Players"
        prob += lpSum([gk[i] * player_vars[i] for i in player]) == 1, "Only 1 GK"
        prob += lpSum([defe[i] * player_vars[i] for i in player]) <= 5, "Less than 4 DEF"
        prob += lpSum([mid[i] * player_vars[i] for i in player]) <= 5, "Less than 5 MID"
        prob += lpSum([stri[i] * player_vars[i] for i in player]) <= 3, "Less than 3 STR"

    prob += lpSum([cost[i] * player_vars[i] for i in player]) <= my_squad_value + budget, "Total Cost"

    for t in range(1,21):
        prob += lpSum([teams[t][str(i)] * player_vars[i] for i in player]) <= 3, "Less than 3 from team " + str(t)
    
    squad_size = 15 if full_squad else 11 

    prob += lpSum([current_squad[i] * player_vars[i] for i in player]) >= squad_size - transfers, "Keep players"

    # solve
    status = prob.solve()
    print(LpStatus[status])
    
    # Return new squad
    player_indices = []
    for v in prob.variables():
        if v.varValue>0:
            player_indices.append(int(v.name[8:]))

    new_squad = data[data.index.isin(player_indices)].sort_values(["element_type"])
    print(new_squad)

    return

    
if __name__ == '__main__':
    optimumTeam(
        budget = 829,
        number_of_players=None,
        full_squad = False
    )

    # my_squad = [
    #     455, #RP

    #     17, # KT
    #     542, # SR
    #     255, # AR
    #     376, # JB

    #     474, # PN
    #     254, # MS
    #     302, # BF
    #     390, # HMS

    #     164, # DCL
    #     514, # OW

    #     429, #DM
    #     66, # AW
    #     381, # MO
    #     338, # ASM
    # ]

    # best_transfer(
    #             full_squad = True,
    #             squad = my_squad,
    #             budget = 3,
    #             transfers = 1 
    # )