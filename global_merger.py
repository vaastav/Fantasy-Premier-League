from mergers import *

def merge_data():
    """ Merge all the data and export to a new file
    """
    season_latin = ['2016-17', '2017-18', '2018-19', '2019-20', '2020-21', '2021-22'] 
    encoding_latin = ['latin-1', 'latin-1', 'latin-1', 'utf-8', 'utf-8', 'utf-8']

    dfs = []
    for i,j in zip(season_latin, encoding_latin):
        data = pd.read_csv(import_merged_gw(season=f'{i}'), encoding=f'{j}')
        data['season'] = i
        dfs.append(data)

    df = pd.concat(dfs, ignore_index=True, sort=False)
    df = df[['season','name', 'position', 'team', 'assists','bonus','bps','clean_sheets','creativity','element','fixture','goals_conceded','goals_scored','ict_index','influence','kickoff_time','minutes','opponent_team','own_goals','penalties_missed','penalties_saved','red_cards','round','saves','selected','team_a_score','team_h_score','threat','total_points','transfers_balance','transfers_in','transfers_out','value','was_home','yellow_cards','GW']]

    df = clean_players_name_string(df, col='name')
    df = filter_players_exist_latest(df, col='position')
    df = get_opponent_team_name(df)

    df = df[['season_x', 'name', 'position', 'team_x', 'assists', 'bonus', 'bps',
       'clean_sheets', 'creativity', 'element', 'fixture', 'goals_conceded',
       'goals_scored', 'ict_index', 'influence', 'kickoff_time', 'minutes',
       'opponent_team', 'opp_team_name', 'own_goals', 'penalties_missed', 'penalties_saved',
       'red_cards', 'round', 'saves', 'selected', 'team_a_score',
       'team_h_score', 'threat', 'total_points', 'transfers_balance',
       'transfers_in', 'transfers_out', 'value', 'was_home', 'yellow_cards',
       'GW']]
    
    export_cleaned_data(df)

def main():
    merge_data()

if __name__ == "__main__":
    main()