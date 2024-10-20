#!/usr/bin/env python

import json
import os
import boto3
from config import logger
import fantasy_api as fantasyapi
import utils
import yahoo_oauth as yOauth
import config
import time
import async_task as at

def lambda_handler(event, context):

    logger.debug(event)
    # print(context)

    path = event['rawPath']
    logger.debug('rawPath: %s', path)

    sessionId = utils.getSessionIdFromCookies(event['cookies'])
    logger.debug('SessionId: %s', sessionId)
    valid, access_token = yOauth.isValidSession(sessionId)

    if path =='/login':
        # if already have a valid session, then don't need to login again, just redict to main page
        if valid == True:
            return {
                "isBase64Encoded": False,
                "statusCode": 302,
                "headers": {
                    "Location": config.BASE_URL
                },
                "body": ""
            }
        else:
            return yOauth.login()

    elif path == '/callback':
        # if already have a valid session, then actually the callback method should not be called, redict to main page
        if valid == True:
            return {
                "isBase64Encoded": False,
                "statusCode": 302,
                "headers": {
                    "Location": config.BASE_URL
                },
                "body": ""
            }
        else:
            return yOauth.callback(event['rawQueryString'])

    # for routes other than login and callback, we must need a valid session
    # so if it is not valid, need to redirect to login
    if valid == False:
        logger.debug('Invalid SessionId: %s, rediect to login page.', sessionId)
        return {
            "isBase64Encoded": False,
            "statusCode": 302,
            "headers": {
                "Location": f'{os.environ.get("BASE_URL")}/login'
            }
        }

    # now we have valid session, so we can proceed

    # set access token for the fantasy api module
    fantasyapi.ACCESS_TOKEN = access_token

    
    if path =='/api/leagues':

        leagues = fantasyapi.get_leagues()
        return {
            'statusCode': 200,
            'body': json.dumps(leagues)
        }

    elif path == '/api/analyze':

        body = event['body']
        if type(body) == str:
            body = json.loads(body)
        
        league_key = body['league_key']
        league_id = body['league_id']
        week = int (body['week'])

        season = utils.getDefaultSeason()
        taskId = f"task_{season}_{league_id:08d}_{week:02d}"

        parms = {
            "taskId": taskId,
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
        table = dynamodb.Table(config.DB_Task_Table) 

        resp  = table.get_item(Key={"taskId": taskId})
        if 'Item' in resp:
            status = resp['Item']['status']
            if status == 'COMPLETED':
                last_updated = int(resp['Item']['last_updated'])
                now = int(time.time())
                 # still less than 10 minutes after last update, consider it as up to date
                if now - last_updated < 600: 
                    return {
                        'statusCode': 200,
                        'body': json.dumps(status)
                    }
                else: # consider it as out of date, need to run analysis again
                    at.runAnalysis(parms)
                    return {
                        'statusCode': 202,
                        'body': json.dumps('INITIATED')
                    }
            # we only have three status, 'INITIATED', 'IN PROGRESS', 'COMPLETED'
            # so this should be either 'INITIATED' or 'IN PROGRESS'
            else: 
                return {
                    'statusCode': 202,
                    'body': json.dumps(status)
                }
        # no task id found in db, that means this is the first time to run
        else:
            at.runAnalysis(parms)
            return {
                'statusCode': 202,
                'body': json.dumps('INITIATED')
            }       

    
    else:
        return {
            'statusCode': 501,
            'body': json.dumps('No handler found for route {path}')
        }  

 