#!/usr/bin/env python

import json
import os
import boto3
import time


import utils
import fantasy_api as fapi
import config as cfg

logger = cfg.logger

import yahoo_oauth as yOauth

def lambda_handler(event, context):

    logger.debug(event)
    # logger.debug(context)

    path = event['rawPath']
    logger.debug('rawPath: %s', path)

    if path =='/login':
        return yOauth.login()

    if path == '/callback':
        return yOauth.callback(event['rawQueryString'])

    sessionId = get_session_id_from_cookies(event)
    logger.debug('SessionId: %s', sessionId)
    valid, access_token, user_info = utils.is_valid_session(sessionId)

    if path == '/check_auth':
        if valid == True:
            return {
                'statusCode': 200,
                'body': json.dumps(user_info, ensure_ascii=False, indent=4)
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps("not authenticated")
            }
    
    if path == '/logout':
        if valid == True:
            # remove session from db
            remove_session(sessionId)

            return {
                'statusCode': 200,
                'body': json.dumps("Successfully logged out")
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps("not authenticated")
            }


    # for routes other than login/callback/check_auth/logout, we must need a valid session
    # so if it is not valid, return 401
    if valid == False:
        logger.debug(f'Not authenticated: Invalid SessionId: {sessionId}.')
        return {
            'statusCode': 401,
            'body': json.dumps("not authenticated")
        }

    # now we have valid session, so we can proceed

    # set access token for the fantasy api module
    fapi.set_access_token(access_token)
    
    if path =='/api/leagues':

        leagues = fapi.get_leagues()
        return {
            'statusCode': 200,
            'body': json.dumps(leagues)
        }

    elif path == '/api/getdata':

        qs  = event.get('queryStringParameters')
        if 'league_key' not in qs or 'league_id' not in qs or 'week' not in qs :
            logger.error('Missing parameters in query string, requirede parameters: league_key, league_id, week')
            return
    
        league_key = qs['league_key']
        league_id = int(qs['league_id'])
        week = int (qs['week'])
        season = utils.get_season()
        taskId = f"task_{season}_{league_id:08d}_{week:02d}"
        parms = {
            "sessionId": sessionId,
            "league_key": league_key,
            "league_id": league_id,
            "week": week
        }


        # The analysis task takes time, so we would first try to check if there is 
        # already up to date result cached, if so just return that result.
        # Then we need to check wether there is already a task in progress, if so
        # just return a status saying in process
        # last, we will initialize an async task, then retun status

        dynamodb = boto3.resource('dynamodb') 
        table = dynamodb.Table(os.environ.get("DB_TASK_TABLE")) 
        resp  = table.get_item(Key={"taskId": taskId})
        if 'Item' in resp:
            state = resp['Item']['state']
            percentage = int(resp['Item']['percentage'])
            last_updated = int(resp['Item']['last_updated'])
            now = int(time.time())
            if state == 'COMPLETED':
                 # still less than 10 minutes after last update, consider it as up to date
                if now - last_updated < 600: 
                    return {
                        'statusCode': 200,
                        'body': json.dumps({ "state": state })
                    }
                else: # consider it as out of date, need to run analysis again
                    return run_analysis(parms)
            
            # we only have three status, 'INITIATED', 'IN PROGRESS', 'COMPLETED'
            # so this should be either 'INITIATED' or 'IN PROGRESS', no need to run again
            else: 
                if now - last_updated > 180: # if last update time is more than 3 minutes, we consider it as timeout, need to rerun
                    return run_analysis(parms)
                else:
                    return {
                        'statusCode': 202,
                        'body': json.dumps({ "state": state, "percentage": percentage })
                    }
        # no task id found in db, that means this is the first time to run
        else:
            return run_analysis(parms)

    # for other routes, we don't have handler yet
    else:
        return {
            'statusCode': 501,
            'body': json.dumps(f'No handler found for route {path}')
        }  


def  run_analysis(parms):

    lambda_client = boto3.client('lambda')

    # Prepare the payload
    payload = json.dumps(parms)

    lambda_client.invoke(
        FunctionName = os.environ.get('TASK_JOB_FUNCTION_NAME'),
        InvocationType = 'Event',  # Asynchronous invocation,
        Payload = payload
    )

    return {
        'statusCode': 202,
        'body': json.dumps({ "state": 'INITIATED' })
    }
      

def get_session_id_from_cookies(event):
    
    sessionId = None

    if 'cookies' in event:
        for cookie in event['cookies']:
            pair = cookie.split('=')
            key = pair[0]
            if key == 'sessionId':
                sessionId = pair[1]
                break

    return sessionId

def remove_session(sessionId):
    dynamodb = boto3.resource('dynamodb') 
    table = dynamodb.Table(os.environ.get("DB_SESSION_TABLE")) 
    table.delete_item(Key={"sessionId": sessionId})


def get_result(league_id, week):

    season = utils.get_season()
    total_stats_csv_file_key = f"{season}/{league_id}/0/stats.csv"
    total_point_csv_file_key = f"{season}/{league_id}/0/roto-point.csv"
    week_stats_csv_file_key = f"{season}/{league_id}/{week}/stats.csv"
    week_point_csv_file_key = f"{season}/{league_id}/{week}/roto-point.csv"
    week_battle_csv_file_key = f"{season}/{league_id}/{week}/h2h-score.csv"

    # bar chart file path
    roto_week_bar_file_path = f"/data/{season}/{league_id}/{week}/roto_bar.png"
    roto_total_bar_file_path = f"/data/{season}/{league_id}/0/roto_bar.png"

    pass