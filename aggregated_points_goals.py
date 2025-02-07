import pandas as pd
import numpy as np

def modifyTable(data):
    team_matches = data.drop_duplicates(subset=['season_x','team_x','GW']).copy()
    
    team_matches.loc['points'] = 0
    for index,row in team_matches.iterrows():
        isHome = row['was_home']
        if row['team_h_score'] > row['team_a_score']:
            team_matches.loc[index,'points'] = 3 - (0 if isHome else 3)
        elif row['team_a_score'] > row['team_h_score']:     
            team_matches.loc[index,'points'] = 0 + (0 if isHome else 3)
        else:
            team_matches.loc[index,'points'] = 1  
    team_matches.loc[:,'points'] = team_matches.groupby(['team_x','season_x'])['points'].cumsum()    

    team_matches['team_goals_scored'] = 0
    team_matches['team_goals_conceded'] = 0

    for index,row in team_matches.iterrows():
        team_matches.loc[index,'team_goals_scored'] = team_matches.loc[index,'team_h_score'] if row['was_home'] else team_matches.loc[index,'team_a_score']
        team_matches.loc[index,'team_goals_conceded'] = team_matches.loc[index,'team_a_score'] if row['was_home'] else team_matches.loc[index,'team_h_score']

    team_matches['team_goals_scored'] = team_matches.groupby(['team_x','season_x'])['team_goals_scored'].cumsum()
    team_matches['team_goals_conceded'] = team_matches.groupby(['team_x','season_x'])['team_goals_conceded'].cumsum()
    team_matches['team_goals_diff'] = team_matches['team_goals_scored'] - team_matches['team_goals_conceded']
    newData = data.merge(team_matches[['season_x','GW','team_x','points','team_goals_scored','team_goals_conceded','team_goals_diff']], on=['season_x','GW','team_x'],how='left')
    return newData


def main():
    data = pd.read_csv('data/cleaned_merged_seasons.csv')
    newData = modifyTable(data)
    newData.to_csv('data/cleaned_merged_seasons_team_aggregated.csv',index=False)

if __name__ == '__main__':
    main()

