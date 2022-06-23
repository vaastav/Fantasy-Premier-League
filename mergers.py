from numpy.lib.index_tricks import _diag_indices_from
import pandas as pd 
import numpy as np
from os.path import dirname, join
import os

def import_merged_gw(season='2021-22'):
    """ Function to call merged_gw.csv file in every data/season folder
    Args:
        season (str): Name of the folder season that contains the merged_gw.csv file
    """

    path = os.getcwd()
    filename = 'merged_gw.csv'
    season_path = join(dirname(dirname("__file__")), path, 'data', season, 'gws', filename)
    return season_path

def clean_players_name_string(df, col='name'):
    """ Clean the imported file 'name' column because it has different patterns between seasons

    Args:
        df: merged df for all the seasons that have been imported
        col: name of the column for cleanup
    """
    #replace _ with space in name column
    df[col] = df[col].str.replace('_', ' ')
    #remove number in name column
    df[col] = df[col].str.replace('\d+', '')
    #trim name column
    df[col] = df[col].str.strip()
    return df

def filter_players_exist_latest(df, col='position'):
    """ Fill in null 'position' (data that only available in 20-21 season) into previous seasons. 
        Null meaning that player doesnt exist in latest season hence can exclude.
    """

    df[col] = df.groupby('name')[col].apply(lambda x: x.ffill().bfill())
    df = df[df[col].notnull()]
    return df

def get_opponent_team_name(df):
    """ Find team name from master_team_list file and match with the merged df 
    """

    path = os.getcwd()
    filename = 'master_team_list.csv'
    team_path = join(dirname(dirname("__file__")), path, 'data', filename)
    df_team = pd.read_csv(team_path)

    #create id column for both df_team and df
    df['id'] = df['season'].astype(str) + '_' + df['opponent_team'].astype(str)
    df_team['id'] = df_team['season'].astype(str) + '_' + df_team['team'].astype(str)

    #merge two dfs
    df = pd.merge(df, df_team, on = 'id', how = 'left')

    #rename column
    df = df.rename(columns={"team_name": "opp_team_name"})
    return df

def export_cleaned_data(df):
    """ Function to export merged df into specified folder
    Args:
        path (str): Path of the folder
        filename(str): Name of the file
    """

    path = os.getcwd()
    filename = 'cleaned_merged_seasons.csv'
    filepath = join(dirname(dirname("__file__")), path, 'data', filename)
    df.to_csv(filepath, encoding = 'utf-8')
    return df
