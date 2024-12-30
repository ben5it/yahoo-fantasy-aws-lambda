#!/usr/bin/env python
from datetime import datetime, timedelta, timezone
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
    logger.info('rawPath: %s', path)

    if path =='/api/login':
        return yOauth.login()

    if path =='/api/callback':
        return yOauth.callback(event['rawQueryString'])

    sessionId = get_session_id_from_cookies(event)
    logger.debug('SessionId: %s', sessionId)
    valid, access_token, user_info = utils.is_valid_session(sessionId)

    if path =='/api/check_auth':
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
    
    if path =='/api/logout':
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
        if 'league_id' not in qs:
            logger.error('Missing required parameter "league_id" in query string')
            return {
                'statusCode': 400,
                'body': json.dumps('Missing required parameter "league_id" in query string')
            }  
    
        league_id = int(qs['league_id'])
        week = int(qs['week']) if 'week' in qs else utils.get_default_week(league_id)
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
            item = resp['Item']
            state = item['state']
            percentage = int(item['percentage'])
            status = { "state": state, "percentage": percentage }
            last_updated = int(item['last_updated'])
            now = int(time.time())
            if state == 'COMPLETED':
                week_status = item.get('week_status')

                # would like to avoid unnecessary analysis, there are three cases to consider
                # 1. postevent: the data is already updated after the week ends 
                # 2. midevent: 
                #    a. the data is updated in less than 30 minute, we can consider it 'as' up to date
                #    b. the data is updated after the prior NBA match , and now is before the next match,
                #       so there is no match played after the data is updated, we can consider it as up to date
                #       But we have no way to get the time of prior NBA match played, and the time of the next match.
                #       so we use a workaround here.
                #       the NBA match is usually played in the evening, starting from 7:00 AM to 13:00 PM (China time)
                #       so if the last updated time is after 13:00 PM, and now is before 7:00 AM,  
                #       and now - last_update < 1 day, we can consider it as up to date
                # 
                #  so we can't check this case
                # if it is postevent, then that means the data is already updated after the week ends
                # otherwise, check the last updated time, if it is still less than 15 minutes after last update,
                # consider it as up to date because we don't want to run the analysis too frequently
                should_run_analysis = True
                if week_status == 'postevent':
                    should_run_analysis = False
                else:
                    if now - last_updated < 900: 
                        should_run_analysis = False
                    elif now - last_updated < 86400: # 1 day
                        # Define the Shanghai timezone offset
                        shanghai_timezone = timezone(timedelta(hours=8))
                        # utc_zone = timezone.utc
                        
                        last_update_hour = datetime.fromtimestamp(last_updated, shanghai_timezone).hour
                        now_hour = datetime.fromtimestamp(now, shanghai_timezone).hour
                        if last_update_hour > 13 and (now_hour >= last_update_hour or now_hour < 7):
                            should_run_analysis = False


                if should_run_analysis == False:
                    return get_result(league_id, week, status)
                else: 
                    return run_analysis(parms)
            
            # we only have three status, 'INITIATED', 'IN PROGRESS', 'COMPLETED'
            # so this should be either 'INITIATED' or 'IN PROGRESS', no need to run again
            else: 
                # if there is no update in more than 4 minutes, then maybe a problem already occurs, need to re-run
                if now - last_updated > 240: 
                    return {
                        'statusCode': 501,
                        'body': json.dumps("Server error, please try again later. If problem persists, please contact the administrator.")
                    }
                else:
                    return get_result(league_id, week, status)
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


def get_result(league_id, week, status):

    # the state and percentage determines what data is available
    state = status.get('state', 'INITIATED')
    percentage = status.get('percentage', 0)

    resp_code = 200 if state == 'COMPLETED' else 202

    resp_data = {
        "league_id": league_id,
        "week": week,
        'result': {},
        **status
    }


    season = utils.get_season()
    # base_url = os.environ.get("BASE_URL") + "/"
    week_prefix =   f"data/{season}/{league_id}/{week}/"
    season_prefix =  f"data/{season}/{league_id}/season/"
    
    # week data is only available when the analysis is completed or in progress with more than 25% done
    # here 25% needs to be synced with the value in the long running task
    if state == 'COMPLETED' or ( state == 'IN_PROGRESS' and percentage > 25):
        radar_charts = get_files_with_pattern(week_prefix, "radar_team_")
        resp_data['result']['week'] = {
                "roto_bar": week_prefix + "roto_bar.png",
                "roto_stats": week_prefix + "roto_stats.html",
                "roto_point": week_prefix + "roto_point.html",
                "matchup_score": week_prefix + "matchup_score.html",
                "radar_charts": radar_charts
        }

    # total data is only available when the analysis is completed or in progress with more than 50% done
    # here 50% needs to be synced with the value in the long running task
    if state == 'COMPLETED' or ( state == 'IN_PROGRESS' and percentage >= 50):
        radar_charts = get_files_with_pattern(season_prefix, "radar_team_")
        resp_data['result']['total'] = {
                "roto_bar": season_prefix + "roto_bar.png",
                "roto_stats": season_prefix + "roto_stats.html",
                "roto_point": season_prefix + "roto_point.html",
                "radar_charts": radar_charts
        }

    # cumulative data is only available when the analysis is completed or in progress with more than 75% done
    # here 75% needs to be synced with the value in the long running task
    if state == 'COMPLETED' or ( state == 'IN_PROGRESS' and percentage >= 75):
        pie_charts = get_files_with_pattern(season_prefix, "pie_chart_")
        resp_data['result']['cumulative'] = {
                "rank_trend": season_prefix + "rank_trend.png",
                "point_trend": season_prefix + "point_trend.png",
                "score_trend": season_prefix + "score_trend.png",
                "standing": season_prefix + "standing.html",
                "median_diff_trend": season_prefix + "median_diff_trend.html",
                "total_diff_trend": season_prefix + "total_diff_trend.html",
                "pie_charts": pie_charts
        }

    # forecast data is only available when the analysis is completed
    if state == 'COMPLETED': 
        resp_data['result']['forecast'] = get_files_with_pattern(season_prefix, "radar_forecast_")

    # logger.info(json.dumps(resp_data, ensure_ascii=False, indent=4))
    return {
        'statusCode': resp_code,
        'body': json.dumps(resp_data, ensure_ascii=False, indent=4)
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