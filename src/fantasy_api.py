import json
# import os
import requests
from urllib.parse import parse_qs
# import logging
# import base64
# import jwt
# import time
# import uuid
# import boto3
# from decimal import Decimal
# import config
import objectpath

import pandas as pd
from pandas import DataFrame

import utils
import config
from config import logger

ACCESS_TOKEN = ''

def get_leagues():
    '''
    Return all leagues of current user for the recent season
    '''
    season = utils.getDefaultSeason()
    logger.debug('get leagues for season {}'.format(season))

    uri = 'users;use_login=1/games;game_codes=nba;seasons={}/leagues'.format(season)
    resp = get_request(uri)
    t = objectpath.Tree(resp)
    jfilter = t.execute('$..leagues..(league_key, league_id, name, logo_url, scoring_type, start_date, end_date, current_week, start_week, end_week)')

    leagues = []
    for l in jfilter:
        leagues.append(l)

    # sort by league id
    leagues.sort(key = lambda league : int(league['league_id']))

    logger.debug('leagues')
    logger.debug(leagues)

    # [{"league_key": "428.l.7124", "league_id": "7124", "name": "Never Ending", "logo_url": false, "scoring_type": "head", "start_date": "2023-10-24", "end_date": "2024-04-14", "current_week": 24, "start_week": "1", "end_week": "24"}, {"league_key": "428.l.23476", "league_id": "23476", "name": "2023~2024 Gamma", "logo_url": "https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/88a86479d6cf4bc472623e59484ab6c70e397336290032a9c744125e158d2c21.jpg", "scoring_type": "head", "start_date": "2023-10-24", "end_date": "2024-04-14", "current_week": 24, "start_week": "1", "end_week": "24"}]

    return leagues


def analyze(body):

    
    logger.debug('request data for analyze：')
    logger.debug(body)

    if 'league_key' in body and 'week' in body and 'league_id' in body:

        league_key = body['league_key']
        league_id = body['league_id']
        week = int (body['week'])
    
        game_stat_categories = get_game_stat_categories()
        teams = get_league_teams(league_key, league_id)

        league_total_stats = []
        league_week_stats = []
        for team in teams:
            # get stat of a team for the total season
            team_total_stat, data_types, sort_orders, point = get_team_stat(team['team_key'], game_stat_categories, 0)
            league_total_stats.append(team_total_stat)

            # get stat of a team for a specified week
            team_week_stat, data_types, sort_orders, point  = get_team_stat(team['team_key'], game_stat_categories, week)
            league_week_stats.append(team_week_stat)

        stat_names = league_week_stats[0].keys()
        team_names = list(map(lambda x: x['name'], teams))
        
        week_df = pd.DataFrame(columns=stat_names, index=team_names)
        week_df.columns.name = 'Team Name'
        total_df = pd.DataFrame(columns=stat_names, index=team_names)
        total_df.columns.name = 'Team Name'

        for idx, team_name in enumerate(team_names):
            team_stat = league_week_stats[idx]
            total_stat = league_total_stats[idx]
            week_df.loc[team_name] = pd.Series(team_stat)
            total_df.loc[team_name] = pd.Series(total_stat)

        week_df = week_df.astype(data_types)
        total_df = total_df.astype(data_types)

        season = utils.getDefaultSeason()
        week_stats_csv_file_key = f"data/{season}/{league_id}/{week}/stats.csv"
        utils.write_dataframe_to_csv_on_s3(week_df, week_stats_csv_file_key)

        total_stats_csv_file_key = f"data/{season}/{league_id}/0/stats.csv"
        utils.write_dataframe_to_csv_on_s3(total_df, total_stats_csv_file_key)

        week_score = utils.stat_to_score(week_df, sort_orders)
        total_score = utils.stat_to_score(total_df, sort_orders)
        week_score_csv_file_key = f"data/{season}/{league_id}/{week}/roto-score.csv"
        utils.write_dataframe_to_csv_on_s3(week_score, week_score_csv_file_key)

        total_score_csv_file_key = f"data/{season}/{league_id}/0/roto-score.csv"
        utils.write_dataframe_to_csv_on_s3(total_score, total_score_csv_file_key)

        league_stat_categories = get_league_stat_categories(league_key)


    
    # parms = parse_qs(queryString)

    # if 'code' not in parms:
    #     logger.error("Code Missing in query string.")

    return {
        'statusCode': 200,
        'body': 'Analyze' 
    }

def get_league_stat_categories(league_key):
    pass

def get_league_teams(league_key, league_id):

    # if data already cached in s3, read from s3;
    # otherwise retirive from yahoo and save to s3
    season = utils.getDefaultSeason()
    file_path = f"data/{season}/{league_id}/teams.json"
    teams = utils.load_json_from_s3(file_path)
    if teams is not None:
        logger.debug(json.dumps(teams, indent=4))  
    else:
        logger.debug("Try to retrive leagues teams from yahoo.")
        uri = f"league/{league_key}/teams"
        resp = get_request(uri)
        t = objectpath.Tree(resp)
        jfilter = t.execute('$..teams..team..(team_key, team_id, name, team_logos)')
        teams = []

        t = {}
        for p in jfilter:
            # logger.debug(p)
            if ('team_logos' in p):
                t['team_logos'] = p['team_logos'][0]['team_logo']['url']
            else:
                t.update(p)

            # team logo is the last property
            if ('team_logos' in t):
                teams.append(t)
                t = {} 

        # # sort by team id
        teams.sort(key = lambda team : int(team['team_id']))

        logger.debug('teams')
        logger.debug(teams)
        utils.write_json_to_s3(teams, file_path)
    
    return teams


def get_team_stat(team_key, game_stat_categories, week=0):
    '''
    Return the stats of a team for a certain week, or the season(week==0)
    '''
    if week==0:
        uri = 'team/{}/stats;type=season'.format(team_key)
    else:
        uri = 'team/{}/stats;type=week;week={}'.format(team_key, week)
    # logger.debug(uri)
    resp = get_request(uri)
    # logger.debug(resp)
    t = objectpath.Tree(resp)
    jfilter = t.execute('$..team_stats..stats..(stat_id, value)')

    stats = {}
    data_types = {}
    sort_orders = []
    for s in jfilter:
        stat_id = s['stat_id']

        # make sure stat_id in game stat categories to filter out display only stat
        if stat_id in game_stat_categories:
            stat_name = game_stat_categories[stat_id]['display_name']
            v = s['value']
            if isinstance(v, str) and '.' in v:
                v = float(v)
                data_types[stat_name] ='float'
            else:
                v = int(v)
                data_types[stat_name] = 'int'

            stats[stat_name] = v

            sort_order = game_stat_categories[stat_id]['sort_order']
            sort_orders.append(sort_order)

    # logger.debug(stats)
    # {'FG%': 0.455, 'FT%': 0.746, '3PTM': 32, 'PTS': 322, 'OREB': 48, 'REB': 177, 'AST': 82, 'ST': 17, 'BLK': 17, 'TO': 38, 'A/T': 2.16}
    # logger.debug(data_types)
    # {'FG%': 'float', 'FT%': 'float', '3PTM': 'int', 'PTS': 'int', 'OREB': 'int', 'REB': 'int', 'AST': 'int', 'ST': 'int', 'BLK': 'int', 'TO': 'int', 'A/T': 'float'}
    # logger.debug(sort_orders)
    # ['1', '1', '1', '1', '1', '1', '1', '1', '1', '0', '1']


    if week==0:
        return stats, data_types, sort_orders, None
    else:
        # for a single week, need to get the current point 
        point = 0
        result = t.execute('$..team_points.total')
        for entry in result:
            point = (float)(entry)
            break

        return stats, data_types, sort_orders, point

def get_game_stat_categories():
    '''
    Return all available stat categories of the game(NBA),
    used to dynamically create the stat table.
    '''
    logger.debug("get_game_stat_categories")
    
    # if data already cached in s3, read from s3;
    # otherwise retirive from yahoo and save to s3
    file_path = 'data/game_stat_categories.json'
    categories = utils.load_json_from_s3(file_path)
    if categories is not None:
        logger.debug(json.dumps(categories, indent=4))  
    else:
        logger.debug("Try to retrive game stat categories from yahoo.")
        categories = {}
        uri = 'game/nba/stat_categories'
        resp = get_request(uri)
        t = objectpath.Tree(resp)
        jfilter = t.execute('$..stat_categories..stats..(stat_id, display_name, sort_order)')

        for c in jfilter:
            if 'stat_id' in c and 'display_name' in c and 'sort_order' in c:
                categories[c['stat_id']] = c

        logger.debug('categories')
        logger.debug(categories)
        utils.write_json_to_s3(categories, file_path)
    
    return categories

def get_league_matchup( league_teams, week):
    pass


def get_request(path): 
    """Send an API request to the URI and return the response as JSON

    :param uri: URI of the API to call
    :type uri: str
    :return: JSON document of the response
    :raises: RuntimeError if any response comes back with an error
    """
    url = f'{config.FANTASY_API_URL}/{path}'
    logger.debug(f'request url: {url}')

    headers = {
        'Authorization': 'Bearer ' + ACCESS_TOKEN
    }

    response = requests.get(url, params={'format': 'json'}, headers = headers)

    if response.status_code != 200:
        logger.error('request to {} failed with error code {}'.format(url, response.status_code))
        raise RuntimeError(response.content)

    jresp = response.json()
    return jresp