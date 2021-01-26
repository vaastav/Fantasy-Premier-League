import pandas as pd
import sys


def pick_team(out, budget, position_column, points_column, name_column, price_column, formation=[4, 4, 2]):
    output_df = out.copy()

    goalkeeper = output_df.where(output_df[position_column] == 1).sort_values(points_column, ascending=False).head(1)
    defenders = output_df.where(output_df[position_column] == 2).sort_values(points_column, ascending=False).head(
        formation[0])
    midfielders = output_df.where(output_df[position_column] == 3).sort_values(points_column, ascending=False).head(
        formation[1])
    strikers = output_df.where(output_df[position_column] == 4).sort_values(points_column, ascending=False).head(
        formation[2])
    team = goalkeeper.append(defenders).append(midfielders).append(strikers)
    print("")
    print("IDEAL TEAM:")
    print("")
    print(team.head(11))
    print("")
    output_df = pd.concat([output_df, team, team]).drop_duplicates(keep=False)
    team_value = team[price_column].sum()

    print("Starting value= " + str(team[price_column].sum()))
    print("Starting points= " + str(team[points_column].sum() + team[points_column].max()))
    print("")

    while team_value >= budget + 0.001:

        potential_replacements = pd.DataFrame(
            columns=['init_name', 'init_price', 'init_points', 'new_name', 'new_price', 'new_points', 'pos'])

        # Find any players in the same position with a lower price, sorted descending
        for index, row in team.iterrows():
            pos = row[position_column]
            price = row[price_column]
            potential_replacement = output_df.where(
                (output_df[position_column] == pos) & (output_df[price_column] < price)).sort_values(points_column,
                                                                                                     ascending=False).head(
                1)
            potential_replacements = potential_replacements.append({
                'init_name': row[name_column],
                'init_price': price,
                'init_points': row[points_column],
                'new_name': potential_replacement.iloc[0][name_column],
                'new_price': potential_replacement.iloc[0][price_column],
                'new_points': potential_replacement.iloc[0][points_column],
                'pos': pos
            }, ignore_index=True)

        potential_replacements['points_hit'] = potential_replacements['init_points'] - potential_replacements[
            'new_points']
        potential_replacements['price_boost'] = potential_replacements['init_price'] - potential_replacements[
            'new_price']
        potential_replacements['points_price_ratio'] = potential_replacements['price_boost'] / potential_replacements[
            'points_hit']

        # potential_replacements = potential_replacements.sort_values(by=['price_boost'], ascending = False)
        # potential_replacements = potential_replacements.sort_values(by=['points_hit'], ascending = True)
        potential_replacements = potential_replacements.sort_values(by=['points_price_ratio'], ascending=False)

        replacement = potential_replacements.iloc[0]
        team_replacement = output_df[output_df['player'] == replacement['new_name']]

        print(
            "Unfortunate " + replacement['init_name'] + " replaced with " + replacement['new_name'] + ", saving " + str(
                replacement['price_boost']) + " but losing " + str(replacement['points_hit']) + " points\n")

        team = team.where(team[name_column] != replacement['init_name']).dropna()
        team = team.append(team_replacement, ignore_index=True)
        output_df = pd.concat([output_df, team, team]).drop_duplicates(keep=False)

        team_value = team[price_column].sum()

    while (team_value <= budget):

        potential_replacements = pd.DataFrame(
            columns=['init_name', 'init_price', 'init_points', 'new_name', 'new_price', 'new_points', 'pos'])

        # Find any players in the same position with a lower price, sorted descending
        for index, row in team.iterrows():
            pos = row[position_column]
            price = row[price_column]
            points = row[points_column]
            potential_replacement = output_df.where(
                (output_df[position_column] == pos) & ((output_df[price_column] - price) <= budget - team_value) & (
                            output_df[points_column] > points)).sort_values(points_column, ascending=False).head(1)
            if not pd.isnull(potential_replacement.iloc[0, 1]):
                potential_replacements = potential_replacements.append({
                    'init_name': row[name_column],
                    'init_price': price,
                    'init_points': row[points_column],
                    'new_name': potential_replacement.iloc[0][name_column],
                    'new_price': potential_replacement.iloc[0][price_column],
                    'new_points': potential_replacement.iloc[0][points_column],
                    'pos': pos
                }, ignore_index=True)

        potential_replacements['points_boost'] = potential_replacements['new_points'] - potential_replacements[
            'init_points']
        potential_replacements['price_hit'] = potential_replacements['new_price'] - potential_replacements['init_price']
        potential_replacements['points_price_ratio'] = potential_replacements['points_boost'] / potential_replacements[
            'price_hit']

        # potential_replacements = potential_replacements.sort_values(by=['points_boost', 'price_hit'], ascending = False)
        potential_replacements = potential_replacements.sort_values(by=['points_boost', 'points_price_ratio'],
                                                                    ascending=False)

        # print(potential_replacements)

        if potential_replacements.empty:
            break

        replacement = potential_replacements.iloc[0]
        team_replacement = output_df[output_df['player'] == replacement['new_name']]

        print(
            "Fortunate " + replacement['init_name'] + " replaced with " + replacement['new_name'] + ", costing " + str(
                replacement['price_hit']) + " but gaining " + str(replacement['points_boost']) + " points")

        team = team.where(team[name_column] != replacement['init_name']).dropna()
        team = team.append(team_replacement, ignore_index=True)
        output_df = pd.concat([output_df, team, team]).drop_duplicates(keep=False)

        team_value = team[price_column].sum()

    print("")
    print("TEAM AFTER TRANSFERS:")
    print("")
    print(team)
    print("")

    print("Final value= " + str(team[price_column].sum()))
    print("Final (predicted) points= " + str(team[points_column].sum() + team[points_column].max()))
    print("")

    return team


def pick_transfers(team, out, budget, position_column, points_column, name_column, price_column, formation=[4, 4, 2],
                   max_transfers=1000):
    print("")
    print("TEAM BEFORE TRANSFERS:")
    print("")
    print(team)
    print("")
    print("Starting value= " + str(team[price_column].sum()))
    print("Starting points= " + str(team[points_column].sum() + team[points_column].max()))
    print("")

    team_value = team[price_column].sum()
    budget = team_value + budget
    output_df = out.copy()
    output_df = pd.concat([output_df, team, team]).drop_duplicates(subset='player', keep=False)

    transfers = 0

    while (team_value <= budget and transfers < max_transfers):

        transfers = transfers + 1

        potential_replacements = pd.DataFrame(
            columns=['init_name', 'init_price', 'init_points', 'new_name', 'new_price', 'new_points', 'pos'])

        # Find any players in the same position sorted descending
        for index, row in team.iterrows():
            pos = row[position_column]
            price = row[price_column]
            points = row[points_column]
            potential_replacement = output_df.where(
                (output_df[position_column] == pos) & ((output_df[price_column] - price) <= budget - team_value) & (
                            output_df[points_column] > points)).sort_values(points_column, ascending=False).head(1)
            if not pd.isnull(potential_replacement.iloc[0, 1]):
                potential_replacements = potential_replacements.append({
                    'init_name': row[name_column],
                    'init_price': price,
                    'init_points': row[points_column],
                    'new_name': potential_replacement.iloc[0][name_column],
                    'new_price': potential_replacement.iloc[0][price_column],
                    'new_points': potential_replacement.iloc[0][points_column],
                    'pos': pos
                }, ignore_index=True)

        potential_replacements['points_boost'] = potential_replacements['new_points'] - potential_replacements[
            'init_points']
        potential_replacements['price_hit'] = potential_replacements['new_price'] - potential_replacements['init_price']
        potential_replacements['points_price_ratio'] = potential_replacements['points_boost'] / potential_replacements[
            'price_hit']

        # potential_replacements = potential_replacements.sort_values(by=['points_boost', 'price_hit']
        # , ascending = False)
        potential_replacements = potential_replacements.sort_values(by=['points_boost', 'points_price_ratio'],
                                                                    ascending=False)

        # print(potential_replacements)

        if potential_replacements.empty:
            break

        replacement = potential_replacements.iloc[0]
        team_replacement = output_df[output_df['player'] == replacement['new_name']]

        print(replacement['init_name'] + " for " + replacement['new_name'] + " costing " + str(
            replacement['price_hit']) + " and gaining " + str(replacement['points_boost']) + " points")

        #         print(team)
        team = team.where(team[name_column] != replacement['init_name']).dropna()
        #         print(team)
        team = team.append(team_replacement, ignore_index=True)
        #         print(team)
        output_df = pd.concat([output_df, team, team]).drop_duplicates(keep=False)

        team_value = team[price_column].sum()

    print("")
    print("TEAM AFTER TRANSFERS:")
    print("")
    print(team)
    print("")

    print("Final value= " + str(team[price_column].sum()))
    print("Final (predicted) points= " + str(team[points_column].sum() + team[points_column].max()))
    print("")

    return team


def main(save_team, from_scratch, formation, budget, max_transfers):
    source_path = ".../data/"
    source_path2 = ".../Fantasy-Premier-League/data/2020-21/players_raw.csv"
    destination_path = ".../data/"

    predictions = pd.read_csv(source_path + "predictions.csv").drop_duplicates()
    price_list = pd.read_csv(source_path2).drop_duplicates()
    price_list['player'] = price_list['first_name'] + "_" + price_list['second_name']
    price_list['price'] = price_list['now_cost'] / 10
    price_list['position'] = price_list['element_type']
    players = price_list[['player', 'price', 'team', 'position']]
    players = pd.merge(players, predictions, how='inner', left_on=['player', 'position'],
                       right_on=['player', 'position'])
    if from_scratch:
        team = pick_team(players, budget, 'position', 'prediction', 'player', 'price', formation)
    else:
        team = pd.read_csv(source_path + 'selected_team.csv')
        team = pd.merge(team['player'], players, on='player')
        team = pick_transfers(team, players, budget, 'position', 'prediction', 'player', 'price', formation,
                              max_transfers)
    if save_team:
        team.to_csv(source_path + 'selected_team.csv', index=False)


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(
            "Usage: python team_picker.py <save_team> <build_from_scratch> "
            "<formation> <budget> <max_transfers>. Eg: python teams_scraper.py 5000")
        sys.exit(1)
    save_team = sys.argv[1].upper() == "TRUE"
    from_scratch = sys.argv[2].upper() == "TRUE"
    formation = list(map(int, list(sys.argv[3])))
    budget = float(sys.argv[4])
    max_transfers = int(sys.argv[5])
    main(save_team, from_scratch, formation, budget, max_transfers)
