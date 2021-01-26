import pandas as pd
import numpy as np
import os
from config import RAW_DATA_PATH, INGESTED_DATA, FEATURE_DATA, PAST_WEEKS_NUM, BASE_FEATURES


def create_index(df):
    df['career_gw'] = df['season'] + " | " + df['GW'].astype(int).astype(str).str.pad(width=2, fillchar='0')
    return df.set_index(['player', 'career_gw']).sort_index(level=[0, 1])


def add_own_team_features(df):
    df['team_goals_scored'] = np.where(df['was_home'] is True, df['team_h_score'], df['team_a_score'])
    df['team_points'] = np.where(df['was_home'] is True,
                                 np.where(df['team_h_score'] > df['team_a_score'],
                                          3,
                                          np.where(df['team_h_score'] == df['team_a_score'],
                                                   1,
                                                   0)
                                          ),
                                 np.where(df['team_h_score'] > df['team_a_score'],
                                          0,
                                          np.where(df['team_h_score'] == df['team_a_score'],
                                                   1,
                                                   3)
                                          )
                                 )
    return df


def create_feature_over_time(base_features, past_weeks_num, features_df, base_features_df):
    for feat in base_features:
        for x in past_weeks_num:
            post_pend = f"_av_last_{x}_gws"
            features_df[feat + post_pend] = base_features_df.groupby(level=0)[feat].shift(0).rolling(x).mean()
            post_pend = f"_diff_last_{x}_gws"
            features_df[feat + post_pend] = base_features_df.groupby(
                level=0)[feat].shift(0) - base_features_df.groupby(level=0)[feat].shift(x)
        post_pend = "_ewm"
        features_df[feat + post_pend] = base_features_df.groupby(level=0)[feat].shift(0).ewm(com=1).mean()
        post_pend = "_atm"
        features_df[feat + post_pend] = base_features_df.groupby(level=0)[feat].shift(0).expanding().mean()
    return features_df


def main():
    gw_df = pd.read_csv(os.path.join(RAW_DATA_PATH, INGESTED_DATA)).drop_duplicates()

    gw_df_team_features = gw_df.pipe(create_index).pipe(add_own_team_features)

    gw_df_team_features['is_home'] = gw_df_team_features['was_home']

    gw_df_filtered = gw_df_team_features[BASE_FEATURES + ['is_home', 'element_type']]

    features_df = gw_df_filtered[['element_type', 'is_home']]
    features_df['target'] = gw_df_filtered.groupby(level=0)['total_points'].shift(-1)

    features_with_time_df = create_feature_over_time(base_features=BASE_FEATURES, past_weeks_num=PAST_WEEKS_NUM,
                                                     features_df=features_df, base_features_df=gw_df_filtered)

    for col in features_with_time_df.columns.difference(['target']):
        features_with_time_df[col] = features_with_time_df[col].fillna(0).replace([np.inf, -np.inf], 100)

    features_with_time_df = features_with_time_df.drop('is_home', axis=1)
    features_with_time_df = features_with_time_df.reset_index()
    features_with_time_df.drop_duplicates().to_csv(os.path.join(RAW_DATA_PATH, FEATURE_DATA), index=False)


if __name__ == "__main__":
    main()
