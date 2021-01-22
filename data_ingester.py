import pandas as pd
import numpy as np
import os

def gameweek_filepaths(players_path):
    filepaths = []
    for root, dirs, files in os.walk(players_path):
        for filename in files:
            if filename == "gw.csv":
                filepaths += [f"{root}/{filename}"]
    return filepaths

def main():
    
    source_path = ".../Fantasy-Premier-League/data/"
    destination_path = ".../data/"
    feature_columns = ['assists', 'bonus', 'bps', 'clean_sheets', 'creativity', 'element',
       'fixture', 'goals_conceded', 'goals_scored', 'ict_index', 'influence',
       'kickoff_time', 'minutes', 'opponent_team', 'own_goals',
       'penalties_missed', 'penalties_saved', 'red_cards', 'round', 'saves',
       'selected', 'team_a_score', 'team_h_score', 'threat', 'total_points',
       'transfers_balance', 'transfers_in', 'transfers_out', 'value',
       'was_home', 'yellow_cards']
    
    gw_df = pd.DataFrame(columns=feature_columns)
    position_df = pd.DataFrame(columns=['player', 'element_type'])
    
    for subdir in os.listdir(source_path):
        year = int(subdir[:4])
        players_path = source_path + subdir + "/"
        ssn = f'{year}/{(year+1)%100}'
        print(ssn)
        df = pd.read_csv(players_path + "players_raw.csv")[['first_name', 'second_name', 'id', 'element_type']]
        if year >= 2018:
            df['player'] = df['first_name'] + "_" + df['second_name'] + "_" + df['id'].astype(str)
        else:
            df['player'] = df['first_name'] + "_" + df['second_name']
        df = df[['player', 'element_type']]
        position_df = pd.concat([position_df,df]).drop_duplicates().reset_index(drop=True)
        for path in gameweek_filepaths(players_path):
            try:
                df = pd.read_csv(path)[feature_columns]
                df.sort_values(['kickoff_time'], ascending=True)
                df['GW'] = df.index + 1
                df['player'] = path.rsplit('/',2)[1]
                df['season'] = ssn
                gw_df = gw_df.append(df)
            except:
                print(path.rsplit('/',2)[1] + " doesn't have any data in their gw.csv file")
                
    gw_df = pd.merge(gw_df, position_df, on='player')
    
    gw_df.to_csv(destination_path + "gw_raw.csv", index=False)
    
if __name__ == "__main__":
    main()