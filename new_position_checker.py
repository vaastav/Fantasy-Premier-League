import pandas as pd

dataPath = 'data/'

# maps for converting BPS points
scoringBpsMap = {'FWD': {'GKP': -12, 'DEF': -12, 'MID': -6, 'FWD': 0},
                 'MID': {'GKP': -6, 'DEF': -6, 'MID': 0, 'FWD': 6},
                 'DEF': {'GKP': 0, 'DEF': 0, 'MID': 6, 'FWD': 12},
                 'GKP': {'GKP':0, 'DEF': 0, 'MID': 6, 'FWD': 12}}
cleanSheetBpsMap = {'FWD': {'GKP': 12, 'DEF': 12, 'MID': 0, 'FWD': 0},
                    'MID': {'GKP': 12, 'DEF': 12, 'MID': 0, 'FWD': 0},
                    'DEF': {'GKP': 0, 'DEF': 0, 'MID': -12, 'FWD': -12},
                    'GKP': {'GKP': 0, 'DEF': 0, 'MID': -12, 'FWD': -12}}

# maps for converting absolute points
scoringMap = {'FWD': {'GKP': 2, 'DEF': 2, 'MID': 1, 'FWD': 0},
              'MID': {'GKP': 1, 'DEF': 1, 'MID': 0,  'FWD': -1},
              'DEF': {'GKP': 0, 'DEF': 0, 'MID': -1, 'FWD': -2},
              'GKP': {'GKP': 0, 'DEF': 0, 'MID': -1, 'FWD': -2}}
cleanSheetMap = {'FWD': {'GKP': 4, 'DEF': 4, 'MID': 1, 'FWD': 0},
                 'MID': {'GKP': 3, 'DEF': 3, 'MID': 0, 'FWD': -1},
                 'DEF': {'GKP': 0, 'DEF': 0, 'MID': -3, 'FWD': -4},
                 'GKP': {'GKP': 0, 'DEF': 0, 'MID': -3, 'FWD': -4}}
goalsConcededMap = {'FWD': {'GKP': -1, 'DEF': -1, 'MID': 0, 'FWD': 0},
                    'MID': {'GKP': -1, 'DEF': -1, 'MID': 0, 'FWD': 0},
                    'DEF': {'GKP': 0, 'DEF': 0, 'MID': 1, 'FWD': 1},
                    'GKP': {'GKP': 0, 'DEF': 0, 'MID': 1, 'FWD': 1}}


def getGw(seasonString, gwInt):
    return pd.read_csv(f'{dataPath}{seasonString}/gws/gw{gwInt}.csv')


def getGwFixtures(playerID, df):
    return df[df['element'] == playerID]['fixture'].tolist()



def getGwFixtureInfo(df, fixture):
    df = df[df['fixture'] == fixture]
    df = df.set_index('element')
    return df


def recalculateFixtureBonus(df, playerID, newPos):
    oldPos = df.loc[playerID].position
    BPS = df.loc[playerID].bps
    if oldPos == newPos:
        return 0
    BPS += df.loc[playerID].clean_sheets * cleanSheetBpsMap[oldPos][newPos]
    BPS += df.loc[playerID].goals_scored * scoringBpsMap[oldPos][newPos]
    df.loc[playerID, 'bps'] = BPS
    try:
        newBonus = df.nlargest(3, 'bps', keep='all')['bps'].rank(method='max').loc[playerID]
        return int(newBonus - df.loc[playerID].bonus)
    except KeyError:
        return 0


def recalculateFixturePoints(df, playerID, newPos):
    oldPos = df.loc[playerID].position
    points = df.loc[playerID].total_points
    if oldPos == newPos:
        return 0
    points += (df.loc[playerID].clean_sheets * cleanSheetMap[oldPos][newPos])
    points += (df.loc[playerID].goals_scored * scoringMap[oldPos][newPos])
    points += ((df.loc[playerID].goals_conceded // 2) * goalsConcededMap[oldPos][newPos])
    points += recalculateFixtureBonus(df, playerID, newPos)
    return points


def recalculateTotalPoints(seasonString, playerID, newPos):
    newPoints = 0
    oldPoints = 0
    for i in range(1, 39):
        gw = getGw(seasonString, i)
        fixtureList = getGwFixtures(playerID, gw)
        for fixture in fixtureList:
            fx = getGwFixtureInfo(gw, fixture)
            newPoints += recalculateFixturePoints(fx, playerID, newPos)
            oldPoints += fx.loc[playerID].total_points
    return {'old': oldPoints, 'new': newPoints, }


if __name__ == "__main__":
    print(f"Salah (MID to FWD): {recalculateTotalPoints(seasonString='2021-22', playerID=233, newPos='FWD')}")
    print(f"Jota (MID to FWD): {recalculateTotalPoints(seasonString='2021-22', playerID=240, newPos='FWD')}")
    print(f"Havertz (MID to FWD): {recalculateTotalPoints(seasonString='2021-22', playerID=141, newPos='FWD')}")
    print(f"Dallas (MID to DEF): {recalculateTotalPoints(seasonString='2021-22', playerID=188, newPos='DEF')}")
    print(f"Joelinton (FWD to MID): {recalculateTotalPoints(seasonString='2021-22', playerID=310, newPos='MID')}")
    print(f"Saint-Maximan (FWD to MID): {recalculateTotalPoints(seasonString='2021-22', playerID=307, newPos='MID')}")
    print(f"Kouyate (DEF to MID): {recalculateTotalPoints(seasonString='2021-22', playerID=150, newPos='MID')}")
