#!/usr/bin/env python

from datetime import datetime, timedelta, date, timezone
from decimal import Decimal
import base64
import boto3
import json
import os
import requests
import time
import config as cfg
import s3_operation as s3op

logger = cfg.logger



def get_season():
    today =date.today()
    season = today.year
    if today.month < 10 or (today.month == 10 and today.day < 26): # nba season usually starts at the end of Oct
        season -= 1   
    
    return season


def get_default_week(league_id):
    season = get_season()
    league_info_file_key = f"{season}/{league_id}/league_info.json"
    league_info, last_updated = s3op.load_json_from_s3(league_info_file_key)

    current_week = int(league_info['current_week'])
    start_week = int(league_info['start_week'])

    # Define the Pacific timezone offset
    pacific_offset = timedelta(hours=-8)
    pacific_timezone = timezone(pacific_offset)
    
    today = datetime.now(pacific_timezone).date()
    weekday = today.weekday()

    # default week is current week
    default_week = current_week

    # but if it is Mon, set default week to previous week
    if weekday < 1:
        default_week -= 1

    # if default week is less than start week, set it to start week
    if default_week < start_week:
        default_week = start_week

    return default_week

def get_forecast_week(league_id):
    season = get_season()
    league_info_file_key = f"{season}/{league_id}/league_info.json"
    league_info, last_updated = s3op.load_json_from_s3(league_info_file_key)

    current_week = int(league_info['current_week'])
    end_week = int(league_info['end_week'])

    # Define the Pacific timezone offset
    pacific_offset = timedelta(hours=-8)
    pacific_timezone = timezone(pacific_offset)
    
    today = datetime.now(pacific_timezone).date()
    weekday = today.weekday()

    forecast_week = current_week + 1
    # if it is Mon/Tue/Wed, set forecast week to current week
    # because this is used for research the matchup
    if weekday < 3:
        forecast_week -= 1
    if forecast_week > end_week:
        forecast_week = end_week

    return forecast_week

def get_league_info(league_id):
    season = get_season()
    league_info_file_key = f"{season}/{league_id}/league_info.json"
    league_info, last_updated = s3op.load_json_from_s3(league_info_file_key)
    return league_info

def get_task_id(league_id, week):
    season = get_season()
    return f"task_{season}_{league_id:08d}_{week:02d}"


def get_access_token_from_db(sessionId):
    dynamodb = boto3.resource('dynamodb') 
    table = dynamodb.Table(os.environ.get("DB_SESSION_TABLE")) 

    resp  = table.get_item(Key={"sessionId": sessionId})
    if 'Item' in resp:
        return resp['Item']['access_token']
    else:
        return None



def is_valid_session(sessionId):
    
    valid = False
    access_token = None
    user_info = {}

    if sessionId is None or sessionId == '':
        return valid, access_token, user_info

    logger.debug('try to find session in db')        
    dynamodb = boto3.resource('dynamodb') 
    table = dynamodb.Table(os.environ.get("DB_SESSION_TABLE")) 

    resp  = table.get_item(Key={"sessionId": sessionId})
    if 'Item' in resp:
        access_token = resp['Item']['access_token']

        user_info['userId'] = resp['Item']['userId']
        user_info['email'] = resp['Item']['email']
        user_info['nickname'] = resp['Item']['nickname']
        user_info['profile_image'] = resp['Item']['profile_image']

        now = int(time.time())
        expiration_time = float(resp['Item']['expiration_time'])

        if expiration_time - now < 0: 
            logger.debug("Session already expires.  Expiration time: {}, Now:{}".format(datetime.fromtimestamp(expiration_time), datetime.fromtimestamp(now)))
            valid = False
        # expiring soon (in 5 minute), refresh token
        elif expiration_time - now < 300:  
            logger.debug("expiring in 5 minute, need to refresh token.  Expiration time: {}, Now:{}".format(datetime.fromtimestamp(expiration_time), datetime.fromtimestamp(now)))
            current_refresh_token = resp['Item']['refresh_token']
            refresh_token(sessionId, current_refresh_token)
            valid = True
        else:
            logger.debug("Find valid session id db")
            valid = True
    else:
        logger.debug("SessionId {} not found in db".format(sessionId))
        valid = False
    
    return valid, access_token, user_info

def refresh_token(sessionId, current_refresh_token):
    encoded_credentials = base64.b64encode(('{0}:{1}'.format(os.environ.get('CLIENT_ID'), os.environ.get('CLIENT_SECRET'))).encode('utf-8'))

    headers = {
        'Authorization': 'Basic {0}'.format(encoded_credentials.decode('utf-8')),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data =  {
        "refresh_token": current_refresh_token,
        "grant_type": "refresh_token",
        "redirect_uri": os.environ.get('BASE_URL') + "/callback"
    }

    raw_token = requests.post(cfg.ACCESS_TOKEN_URL, data=data, headers = headers)
    parsed_token = raw_token.json()
    logger.debug(parsed_token)
    if 'error' in parsed_token:
        return {
            'statusCode': 401,
            'body': parsed_token['error_description']
        }
    else:
        access_token = parsed_token["access_token"]
        refresh_token = parsed_token["refresh_token"]
        expiration_time = time.time() + parsed_token["expires_in"]

        # update the time to live of this item
        ttl = int((datetime.now() + timedelta(days=1)).timestamp())
        dynamodb = boto3.resource('dynamodb') 
        logger.debug('update access token to dynamodb table %s', os.environ.get("DB_SESSION_TABLE"))
        table = dynamodb.Table(os.environ.get("DB_SESSION_TABLE")) 
        #inserting values into table 
        response = table.update_item(
            Key={'sessionId': sessionId},
            UpdateExpression='SET access_token=:val1, refresh_token=:val2, expiration_time=:val3, expireAt=:val4',
            ExpressionAttributeValues =json.loads(json.dumps({
                ':val1':  access_token,
                ':val2':  refresh_token,
                ':val3':  expiration_time,
                ':val4': ttl
            }), parse_float=Decimal),
            ReturnValues="UPDATED_NEW"
        )
        logger.debug(response["Attributes"])


