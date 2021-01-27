import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn import ensemble
from config import RAW_DATA_PATH, FEATURE_DATA, PREDICTIONS, TARGET_WEEKS_INTO_FUTURE
import os


def main():
    features = pd.read_csv(os.path.join(RAW_DATA_PATH, FEATURE_DATA),
                           index_col=['player', 'career_gw'])
    params = {'n_estimators': 500,
              'max_depth': 4,
              'min_samples_split': 5,
              'learning_rate': 0.01,
              'loss': 'ls'}

    positions = features.element_type.unique()
    pred_pos_dict = {}

    for pos in positions:
        print(pos)
        # Model for each position
        players_in_pos = features[features['element_type'] == pos]

        # Train-test split

        grouped = players_in_pos.reset_index(['career_gw'])
        test = grouped.groupby(level=0).tail(min(1, TARGET_WEEKS_INTO_FUTURE))
        test.set_index('career_gw', append=True, inplace=True)
        # test = players_in_pos.xs(players_in_pos.index.levels[1].max(), level=1, drop_level=False)
        # train = players_in_pos.drop(players_in_pos.index.levels[1].max(), level=1, axis=0)
        train = players_in_pos.drop(test.index)


        # Drops rows with target NA which are not most recent month
        filtered_train = train[train.target.notna()].drop(['element_type', 'team', 'team_code'], axis=1)

        X_train_pd = filtered_train.drop('target', axis=1)
        y_train_pd = filtered_train['target']
        X_test_pd = test.drop(['target', 'element_type', 'team', 'team_code'], axis=1)

        # Normalize
        scaler = StandardScaler()
        scaler.fit(X_train_pd)
        X_train = scaler.transform(X_train_pd)
        y_train = y_train_pd.to_numpy()
        X_test = scaler.transform(X_test_pd)

        # Train model
        reg = ensemble.GradientBoostingRegressor(**params)
        reg.fit(X_train, y_train)

        # Predict
        pred = pd.DataFrame(reg.predict(X_test))
        pred.rename(columns={0: 'prediction'}, inplace=True)
        pred.index = test.index
        pred = pred.merge(test[['element_type', 'team', 'team_code']], left_index=True, right_index=True)
        print(pred.shape)
        pred_sorted = pred.sort_values(by='prediction', ascending=False)
        pred_sorted['pred_rank'] = pred_sorted['prediction'].rank(method='max', ascending=False)
        pred_pos_dict[pos] = pred_sorted
        print(pred_sorted.shape)

    output_preds = pd.concat(pred_pos_dict.values())
    output_preds.drop_duplicates().to_csv(os.path.join(RAW_DATA_PATH, PREDICTIONS), index=True)


if __name__ == "__main__":
    main()
