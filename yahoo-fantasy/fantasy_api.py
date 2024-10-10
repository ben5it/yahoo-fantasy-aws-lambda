# import json
# import os
import requests
# from urllib.parse import urlencode, quote, parse_qs
# import logging
# import base64
# import jwt
# import time
# import uuid
# import boto3
# from decimal import Decimal
# import config
import objectpath

import utils
import config
from config import logger

ACCESS_TOKEN = ''

def get_leagues():
    '''
    Return all leagues of current user for the recent season
    '''
    season = utils.getDefaultSeason()
    logger.info('get leagues for season {}'.format(season))

    uri = 'users;use_login=1/games;game_codes=nba;seasons={}/leagues'.format(season)
    resp = get_request(uri)
    t = objectpath.Tree(resp)
    jfilter = t.execute('$..leagues..(league_key, league_id, name, logo_url, scoring_type, start_date, end_date, current_week, start_week, end_week)')

    leagues = []
    for l in jfilter:
        leagues.append(l)

    # sort by league id
    leagues.sort(key = lambda league : int(league['league_id']))

    logger.info('leagues')
    logger.info(leagues)
    # [{
    #     'league_key': '418.l.23727',
    #     'league_id': '23727',
    #     'name': 'Never Ending',
    #     'logo_url': 'https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/56477424891_aa0cec.png',
    #     'current_week': 2,
    #     'start_week': '1',
    #     'end_week': '23'
    # }, {
    #     'league_key': '418.l.35600',
    #     'league_id': '35600',
    #     'name': 'Hupu Kappa 22-23',
    #     'logo_url': False,
    #     'current_week': 2,
    #     'start_week': '1',
    #     'end_week': '24'
    # }]

    return leagues


def analyze():
    return {
        'statusCode': 200,
        'body': 'Analyze' 
    }

def get_league_stat_categories(league_key):
    pass

def get_league_teams(league_key):
    pass


def get_team_stat(team_key, game_stat_categories, week=0):
    pass

def get_game_stat_categories():

    pass

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
    logger.info(f'request url: {url}')

    headers = {
        'Authorization': 'Bearer ' + ACCESS_TOKEN
    }

    response = requests.get(url, params={'format': 'json'}, headers = headers)

    if response.status_code != 200:
        logger.error('request to {} failed with error code {}'.format(url, response.status_code))
        raise RuntimeError(response.content)

    jresp = response.json()
    return jresp