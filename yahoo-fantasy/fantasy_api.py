# import json
# import os
# import requests
# from urllib.parse import urlencode, quote, parse_qs
# import logging
# import base64
# import jwt
# import time
# import uuid
# import boto3
# from decimal import Decimal
# import config

from config import logger

def get_leagues():
    return {
        'statusCode': 200,
        'body': 'Get Leauges' 
    }

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