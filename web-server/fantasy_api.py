#!/usr/bin/env python

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
import compute as cmpt
import s3_operation as s3op
import chart
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
    resp = make_request(uri)
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

    for league in leagues:
        league_id = league["league_id"]
        league_info_file_key = f"data/{season}/{league_id}/league_info.json"
        s3op.write_json_to_s3(league, league_info_file_key)

    return leagues


# def analyze(body):

    
#     logger.debug('request data for analyze：')
#     logger.debug(body)

#     if 'league_key' in body and 'week' in body and 'league_id' in body:

#         league_key = body['league_key']
#         league_id = body['league_id']
#         week = int (body['week'])
    
#         game_stat_categories = get_game_stat_categories()
#         teams = get_league_teams(league_key, league_id)
#         team_keys = list(map(lambda x: x['team_key'], teams))

#         total_df, sort_orders, points = get_league_stat(team_keys, game_stat_categories, 0)
#         week_df, sort_orders, week_points = get_league_stat(team_keys, game_stat_categories, week)
        
#         week_score = cmpt.stat_to_score(week_df, sort_orders)
#         total_score = cmpt.stat_to_score(total_df, sort_orders)
#         battle_score = cmpt.roto_score_to_battle_score(week_score, week_points)

#         # write to S3
#         season = utils.getDefaultSeason()
#         total_stats_csv_file_key = f"data/{season}/{league_id}/0/stats.csv"
#         total_score_csv_file_key = f"data/{season}/{league_id}/0/roto-score.csv"
#         week_stats_csv_file_key = f"data/{season}/{league_id}/{week}/stats.csv"
#         week_score_csv_file_key = f"data/{season}/{league_id}/{week}/roto-score.csv"
#         week_battle_csv_file_key = f"data/{season}/{league_id}/{week}/battle-score.csv"

#         s3op.write_dataframe_to_csv_on_s3(total_df, total_stats_csv_file_key)
#         s3op.write_dataframe_to_csv_on_s3(total_score, total_score_csv_file_key)
#         s3op.write_dataframe_to_csv_on_s3(week_df, week_stats_csv_file_key)
#         s3op.write_dataframe_to_csv_on_s3(week_score, week_score_csv_file_key)
#         s3op.write_dataframe_to_csv_on_s3(battle_score, week_battle_csv_file_key)

#         predict_week = utils.getPredictWeek(league_id)
#         next_matchups = get_league_matchup(team_keys, predict_week)
#         # matchup_file_path = f"data/{season}/{league_id}/{week}/matchup.json"
#         # s3op.write_json_to_s3(matchup_file_path)

#         # week_bar_chart = chart.league_bar_chart(week_score, '{} 战力榜 - Week {}'.format(league_name, week))
#         # total_bar_chart = chart.league_bar_chart(total_score, '{} 战力榜 - Total'.format(league_name))

#         # radar chart for each team
#         radar_charts = chart.league_radar_charts(week_score, total_score, week)
#         for idx, img_data in enumerate(radar_charts):
#             radar_chart_file_path = f"data/{season}/{league_id}/{week}/chart/r_d_{idx:02d}.png"
#             s3op.write_image_to_s3(img_data, radar_chart_file_path)

#         # matchup prediction for next week
#         next_matchup_charts = chart.next_matchup_radar_charts(total_score, next_matchups, predict_week)
#         for idx, img_data in enumerate(next_matchup_charts):
#             radar_chart_file_path = f"data/{season}/{league_id}/{week}/chart/r_c_{idx:02d}.png"
#             s3op.write_image_to_s3(img_data, radar_chart_file_path)

#     # parms = parse_qs(queryString)

#     # if 'code' not in parms:
#     #     logger.error("Code Missing in query string.")

#     return {
#         'statusCode': 200,
#         'body': 'Analyze' 
#     }

# def get_league_stat_categories(league_key):
#     pass


# def get_league_teams(league_key, league_id):

#     # if data already cached in s3, read from s3;
#     # otherwise retirive from yahoo and save to s3
#     season = utils.getDefaultSeason()
#     file_path = f"data/{season}/{league_id}/teams.json"
#     teams = s3op.load_json_from_s3(file_path)
#     if teams is not None:
#         logger.debug(json.dumps(teams, indent=4))  
#     else:
#         logger.debug("Try to retrive leagues teams from yahoo.")
#         uri = f"league/{league_key}/teams"
#         resp = make_request(uri)
#         t = objectpath.Tree(resp)
#         jfilter = t.execute('$..teams..team..(team_key, team_id, name, team_logos)')
#         teams = []

#         t = {}
#         for p in jfilter:
#             # logger.debug(p)
#             if ('team_logos' in p):
#                 t['team_logos'] = p['team_logos'][0]['team_logo']['url']
#             else:
#                 t.update(p)

#             # team logo is the last property
#             if ('team_logos' in t):
#                 teams.append(t)
#                 t = {} 

#         # # sort by team id
#         teams.sort(key = lambda team : int(team['team_id']))

#         logger.debug('teams')
#         logger.debug(teams)
#         utils.write_json_to_s3(teams, file_path)
    
#     return teams


# def get_league_stat(team_keys, game_stat_categories, week=0):
#     '''
#     Return the stats of a multiple teams for a certain week, or the season(week==0)
#     '''
#     teams_str = ','.join(team_keys)
#     if week==0:
#         uri = f"teams;team_keys={teams_str}/stats;type=season"
#     else:
#         uri = f"teams;team_keys={teams_str}/stats;type=week;week={week}"
#     logger.debug(uri)
#     resp = make_request(uri)
#     tree = objectpath.Tree(resp)
#     jfilter = tree.execute('$..teams..team..team_stats.stats')

#     leagues_stats = []
#     data_types = {}
#     sort_orders = {}
#     for t in jfilter:
#         team_stats = {}
#         for s in t:
#             e = s['stat']
#             stat_id = e['stat_id'] 

#             # make sure stat_id in game stat categories to filter out display only stat
#             if stat_id in game_stat_categories:
#                 stat_name = game_stat_categories[stat_id]['display_name']
#                 v = e['value']
#                 if isinstance(v, str) and '.' in v:
#                     v = float(v)
#                     data_types[stat_name] ='float'
#                 else:
#                     v = int(v)
#                     data_types[stat_name] = 'int'

#                 team_stats[stat_name] = v

#                 sort_order = game_stat_categories[stat_id]['sort_order']
#                 sort_orders[stat_name] = sort_order

#         leagues_stats.append(team_stats)

#     df = pd.DataFrame(leagues_stats)   
#     df = df.astype(data_types)
    
#     jfilter = tree.execute('$..teams..team..name')
#     team_names = []
#     for n in jfilter:
#         team_names.append(n)
#     df['Team'] = team_names
#     df.set_index('Team', inplace=True)

#     jfilter = tree.execute('$..team_points.total')
#     points = []
#     for entry in jfilter:
#         if entry != '':
#             point = (float)(entry)
#             points.append(point)
    
#     logger.debug(df)
#     logger.debug(sort_orders)
#     logger.debug(points)
#     return df, sort_orders, points


# def get_game_stat_categories():
#     '''
#     Return all available stat categories of the game(NBA),
#     used to dynamically create the stat table.
#     '''
#     logger.debug("get_game_stat_categories")
    
#     # if data already cached in s3, read from s3;
#     # otherwise retirive from yahoo and save to s3
#     file_path = 'data/game_stat_categories.json'
#     categories = s3op.load_json_from_s3(file_path)
#     if categories is not None:
#         logger.debug(json.dumps(categories, indent=4))  
#     else:
#         logger.debug("Try to retrive game stat categories from yahoo.")
#         categories = {}
#         uri = 'game/nba/stat_categories'
#         resp = make_request(uri)
#         t = objectpath.Tree(resp)
#         jfilter = t.execute('$..stat_categories..stats..(stat_id, display_name, sort_order)')

#         for c in jfilter:
#             if 'stat_id' in c and 'display_name' in c and 'sort_order' in c:
#                 categories[c['stat_id']] = c

#         logger.debug('categories')
#         logger.debug(categories)
#         s3op.write_json_to_s3(categories, file_path)
    
#     return categories

# def get_league_schedule(league_id):
#     pass

# def get_league_matchup(team_keys, week):
#     '''
#     Return the matchup for a specified week.
#     '''
#     teams_str = ','.join(team_keys)
#     uri = f"teams;team_keys={teams_str}/matchups;weeks={week}"
#     logger.debug(uri) 

#     # week_matchup = {}
#     resp = make_request(uri)
#     logger.debug(resp)
#     tree = objectpath.Tree(resp)
#     # jfilter = tree.execute('$..teams..team..matchups..matchup.(week, week_start, week_end)')
#     # for e in jfilter:
#     #     logger.debug(e)
#     #     # {'week': '2', 'week_start': '2023-10-30', 'week_end': '2023-11-05'}
#     #     week_matchup = e
#     #     break

#     teams = []
#     jfilter = tree.execute('$..teams..team..matchups..matchup..teams..team..name')
#     for e in jfilter:
#         # logger.debug(e)
#         if e not in teams:
#             teams.append(e)
#     logger.debug('Week {} Match up'.format(week))
#     for i in range(0, len(teams), 2 ): 
#         logger.debug('{} VS {}'.format(teams[i], teams[i+1])) 

#     # week_matchup['matchup'] = teams
#     # logger.info(week_matchup) 

#     return teams


def make_request(path): 
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