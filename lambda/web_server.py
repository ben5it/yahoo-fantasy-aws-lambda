#!/usr/bin/env python

import json
import os
import boto3
import time
import io
import zipfile
import base64

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
                'body': json.dumps({'authenticated': True, 'user_info': user_info}, ensure_ascii=False, indent=4)
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({'authenticated': False})
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
            'body': json.dumps(leagues, ensure_ascii=False, indent=4)
        }

    elif path == '/api/getdata':

        qs  = event.get('queryStringParameters')
        if 'league_id' not in qs or 'week' not in qs :
            logger.error('Missing parameters in query string, requirede parameters: league_id, week')
            return {
                'statusCode': 400,
                'body': json.dumps('Missing parameters in query string, requirede parameters: league_id, week')
            }  
    
        league_id = int(qs['league_id'])
        week = int (qs['week'])
        season = utils.get_season()
        taskId = f"task_{season}_{league_id:08d}_{week:02d}"
        parms = {
            "sessionId": sessionId,
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
                 # still less than 15 minutes after last update, consider it as up to date
                if now - last_updated < 900: 
                    return get_result(league_id, week)

                else: # consider it as out of date, need to run analysis again
                    return run_analysis(parms)
            
            # we only have three status, 'INITIATED', 'IN PROGRESS', 'COMPLETED'
            # so this should be either 'INITIATED' or 'IN PROGRESS', no need to run again
            else: 
                if now - last_updated > 60: # if there is no update in more than 1 minute, then maybe a problem already occurs, need to rerun
                    return run_analysis(parms)
                else:
                    return {
                        'statusCode': 202,
                        'body': json.dumps({ "state": state, "percentage": percentage })
                    }
        # no task id found in db, that means this is the first time to run
        else:
            return run_analysis(parms)
        
    elif path == '/api/download':

        qs  = event.get('queryStringParameters')
        if 'league_id' not in qs or 'week' not in qs :
            logger.error('Missing parameters in query string, requirede parameters: league_id, week')
            return {
                'statusCode': 400,
                'body': json.dumps('Missing parameters in query string, requirede parameters: league_id, week')
            }  
    
        league_id = int(qs['league_id'])
        week = int (qs['week'])
        season = utils.get_season()

        bucket_name = os.environ.get("DATA_BUCKET_NAME")
        folder_name = f"data/{season}/{league_id}/{week}/"
        
        # Get the list of files in the specified folder
        s3 = boto3.client('s3')
        objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
        
        # Create an in-memory ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for obj in objects.get('Contents', []):
                file_key = obj['Key']
                
                # Filter for only Excel and PNG files
                if file_key.lower().endswith('.xlsx') or file_key.lower().endswith('.png'):
                    file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
                    file_content = file_obj['Body'].read()
                    # Add the file to the ZIP
                    zip_file.writestr(file_key[len(folder_name):], file_content)

        # Return the ZIP file as a response
        zip_buffer.seek(0)
        zip_base64 = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/zip",
                "Content-Disposition": f"attachment; filename={league_id}_{week}_result.zip"
            },
            "body": zip_base64,
            "isBase64Encoded": True
        }

    # for other routes, we don't have handler yet
    else:
        return {
            'statusCode': 404,
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

    base_url = os.environ.get("BASE_URL") + '/'
    season = utils.get_season()

    prefix = f"data/{season}/{league_id}/{week}/"

    # result excel file key
    result_excel_file_key = prefix + f"{league_id}_{week}_result.xlsx"

    # bar chart file path
    roto_week_bar_file_path = prefix + f"roto_bar_w{week:02d}.png"
    roto_total_bar_file_path = prefix + "roto_bar_total.png"

    radar_chart_teams = get_files_with_pattern(prefix, "radar_team_")
    radar_chart_forcast = get_files_with_pattern(prefix, "radar_forecast_")

    data = {
        "state": 'COMPLETED',
        "league_id": league_id,
        "week": week,
        "result": {
            "result_excel": base_url+ result_excel_file_key,
            "bar_chart_week": base_url+ roto_week_bar_file_path,
            "bar_chart_total": base_url + roto_total_bar_file_path,
            "radar_chart_teams": [ base_url + file_key for file_key in radar_chart_teams ],
            "radar_chart_forecast": [ base_url + file_key for file_key in radar_chart_forcast ]
        }
    }

    return {
        'statusCode': 200,
        'body': json.dumps(data, ensure_ascii=False, indent=4)
    }

def get_files_with_pattern(prefix, pattern):
    """
    Get the list of files with a specific name pattern in an S3 bucket.
    
    Parameters
    ----------
    prefix : str
        The prefix (folder path) to search within the S3 bucket.
    pattern : str
        The name pattern to search for.
    
    Returns
    -------
    list
        A list of file keys that match the specified pattern.
    """
    s3 = boto3.client('s3')
    bucket_name = os.environ.get("DATA_BUCKET_NAME")
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    
    file_keys = []
    for obj in objects.get('Contents', []):
        file_key = obj['Key']
        if pattern in file_key:
            file_keys.append(file_key)
    
    return file_keys