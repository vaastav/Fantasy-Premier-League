WEBSCRAPE_DATA_PATH = "C:/Dev/web_scrape_FPL/data/"
RAW_DATA_PATH = "C:/Dev/Data/Fantasy-Premier-League/"
FEATURE_COLUMNS = ['assists', 'bonus', 'bps', 'clean_sheets', 'creativity', 'element',
                   'fixture', 'goals_conceded', 'goals_scored', 'ict_index', 'influence',
                   'kickoff_time', 'minutes', 'opponent_team', 'own_goals',
                   'penalties_missed', 'penalties_saved', 'red_cards', 'round', 'saves',
                   'selected', 'team_a_score', 'team_h_score', 'threat', 'total_points',
                   'transfers_balance', 'transfers_in', 'transfers_out', 'value',
                   'was_home', 'yellow_cards']

INGESTED_DATA = "gw_raw.csv"
FEATURE_DATA = "features_df.csv"
PREDICTIONS = "predictions.csv"
PAST_WEEKS_NUM = [1, 3, 6, 12]
TARGET_TYPE = "AVG"
TARGET_WEEKS_INTO_FUTURE = 6
BASE_FEATURES = ['assists', 'bonus', 'bps', 'clean_sheets', 'creativity',
                 'goals_conceded', 'goals_scored', 'ict_index', 'influence',
                 'minutes', 'own_goals', 'penalties_missed', 'penalties_saved', 'red_cards', 'saves',
                 'selected', 'threat', 'total_points',
                 'transfers_balance', 'transfers_in', 'transfers_out', 'value',
                 'yellow_cards', 'team_goals_scored', 'team_points']
