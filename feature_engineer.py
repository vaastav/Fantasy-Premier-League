import pandas as pd
import numpy as np
from config import RAW_DATA_PATH

# def has_numbers(input_string):
#     return any(char.isdigit() for char in input_string)
#
#
# def drop_player_number(player):
#     r = player
#     if has_numbers(player):
#         r = player.rsplit('_', 1)[0]
#     return r


def main():
    source_path = RAW_DATA_PATH
    destination_path = RAW_DATA_PATH
    gw_df = pd.read_csv(source_path + "gw_raw.csv").drop_duplicates()
    # gw_df.player = gw_df.player.apply(drop_player_number)
    gw_df['career_gw'] = gw_df['season'] + " | " + gw_df['GW'].astype(int).astype(str).str.pad(width=2, fillchar='0')
    gw_df = gw_df.set_index(['player', 'career_gw']).sort_index(level=[0, 1])
    gw_df['team_goals_scored'] = np.where(gw_df['was_home'] == True, gw_df['team_h_score'], gw_df['team_a_score'])
    gw_df['team_points'] = np.where(gw_df['was_home'] == True,
                                    np.where(gw_df['team_h_score'] > gw_df['team_a_score'],
                                             3,
                                             np.where(gw_df['team_h_score'] == gw_df['team_a_score'],
                                                      1,
                                                      0)
                                             ),
                                    np.where(gw_df['team_h_score'] > gw_df['team_a_score'],
                                             0,
                                             np.where(gw_df['team_h_score'] == gw_df['team_a_score'],
                                                      1,
                                                      3)
                                             )
                                    )
    gw_df['is_home'] = gw_df['was_home']
    gw_features_base = ['assists', 'bonus', 'bps', 'clean_sheets', 'creativity',
                        'goals_conceded', 'goals_scored', 'ict_index', 'influence',
                        'minutes', 'own_goals', 'penalties_missed', 'penalties_saved', 'red_cards', 'saves',
                        'selected', 'threat', 'total_points',
                        'transfers_balance', 'transfers_in', 'transfers_out', 'value',
                        'yellow_cards', 'team_goals_scored', 'team_points']
    gw_df = gw_df[gw_features_base + ['is_home', 'element_type']]

    features = pd.DataFrame(gw_df['is_home'].map({True: 1, False: 0}))
    features['target'] = gw_df.groupby(level=0)['total_points'].shift(-1)
    features['element_type'] = gw_df['element_type']

    past_weeks_num = [1, 3, 6, 12]
    for feat in gw_features_base:
        for x in past_weeks_num:
            post_pend = f"_av_last_{x}_gws"
            features[feat + post_pend] = gw_df.groupby(level=0)[feat].shift(0).rolling(x).mean()
            post_pend = f"_diff_last_{x}_gws"
            features[feat + post_pend] = gw_df.groupby(level=0)[feat].shift(0) - gw_df.groupby(level=0)[feat].shift(x)
        post_pend = "_ewm"
        features[feat + post_pend] = gw_df.groupby(level=0)[feat].shift(0).ewm(com=1).mean()
        post_pend = "_atm"
        features[feat + post_pend] = gw_df.groupby(level=0)[feat].shift(0).expanding().mean()

    for col in features.columns:
        if col != "target":
            features[col] = features[col].fillna(0).replace([np.inf, -np.inf], 100)
    features = features.drop('is_home', axis=1)
    features = features.reset_index()
    features.drop_duplicates().to_csv(destination_path + "features.csv", index=False)


if __name__ == "__main__":
    main()
