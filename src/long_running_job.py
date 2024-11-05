#!/usr/bin/env python
from datetime import datetime, timedelta
import boto3
import json
import os

import chart as chart
import compute as cmpt
import config as cfg
import fantasy_api as fapi
import s3_operation as s3op
import utils

logger = cfg.logger



def lambda_handler(event, context):

    logger.debug(event)

    if 'sessionId' not in event:
        logger.error('Invalid input: sessionId is missing')


    sessionId = event['sessionId']
    valid, access_token, user_info = utils.is_valid_session(sessionId)
    if valid == False:
        logger.error('Invalid session')
        return
    else:
        fapi.set_access_token(access_token)

    if 'league_id' not in event or 'week' not in event :
        logger.error('Invalid input: league_id or week is missing')
        return
    
    league_id = int(event['league_id'])
    week = int(event['week'])

    league_info = utils.get_league_info(league_id)
    league_key = league_info['league_key']

    task_id = utils.get_task_id(league_id, week)
    update_status(task_id, { "state": 'INITIATED' })
   
    game_stat_categories = fapi.get_game_stat_categories()
    teams = fapi.get_league_teams(league_key, league_id)
    team_keys = list(map(lambda x: x['team_key'], teams))
    update_status(task_id, { "state": 'IN PROGRESS', "percentage": 5 })

    total_df, sort_orders = fapi.get_league_stats(team_keys, game_stat_categories, 0)
    week_df, sort_orders  = fapi.get_league_stats(team_keys, game_stat_categories, week)
    update_status(task_id, { "state": 'IN PROGRESS', "percentage": 15 })
    
    week_score = cmpt.stat_to_score(week_df, sort_orders)
    total_score = cmpt.stat_to_score(total_df, sort_orders)
    matchup_arr, matchup_dict = fapi.get_league_matchup(team_keys, week)
    battle_score = cmpt.roto_score_to_battle_score(week_score, matchup_dict)
    update_status(task_id, { "state": 'IN PROGRESS', "percentage": 25 })

    # write to S3
    season = utils.get_season()
    total_stats_csv_file_key = f"{season}/{league_id}/0/stats.csv"
    total_score_csv_file_key = f"{season}/{league_id}/0/roto-point.csv"
    week_stats_csv_file_key = f"{season}/{league_id}/{week}/stats.csv"
    week_score_csv_file_key = f"{season}/{league_id}/{week}/roto-point.csv"
    week_battle_csv_file_key = f"{season}/{league_id}/{week}/h2h-score.csv"

    s3op.write_dataframe_to_csv_on_s3(total_df, total_stats_csv_file_key)
    s3op.write_dataframe_to_csv_on_s3(total_score, total_score_csv_file_key)
    s3op.write_dataframe_to_csv_on_s3(week_df, week_stats_csv_file_key)
    s3op.write_dataframe_to_csv_on_s3(week_score, week_score_csv_file_key)
    s3op.write_dataframe_to_csv_on_s3(battle_score, week_battle_csv_file_key)
    update_status(task_id, { "state": 'IN PROGRESS', "percentage": 35 })

    forecast_week = utils.get_forecast_week(league_id)
    next_matchup_arr, next_matchup_dict = fapi.get_league_matchup(team_keys, forecast_week)
    matchup_file_path = f"{season}/{league_id}/{forecast_week}/matchup.json"
    s3op.write_json_to_s3(next_matchup_arr, matchup_file_path)
    update_status(task_id, { "state": 'IN PROGRESS', "percentage": 50 })

    league_name = utils.get_league_info(league_id)['name']
    week_bar_chart = chart.league_bar_chart(week_score, '{} 战力榜 - Week {}'.format(league_name, week))
    roto_week_bar_file_path = f"{season}/{league_id}/{week}/roto_bar.png"
    s3op.write_image_to_s3(week_bar_chart, roto_week_bar_file_path)
    update_status(task_id, { "state": 'IN PROGRESS', "percentage": 55 })

    total_bar_chart = chart.league_bar_chart(total_score, '{} 战力榜 - Total'.format(league_name))
    roto_total_bar_file_path = f"{season}/{league_id}/0/roto_bar.png"
    s3op.write_image_to_s3(total_bar_chart, roto_total_bar_file_path)
    update_status(task_id, { "state": 'IN PROGRESS', "percentage": 60 })

    # radar chart for each team
    radar_charts = chart.league_radar_charts(week_score, total_score, week)
    for idx, img_data in enumerate(radar_charts):
        radar_chart_file_path = f"{season}/{league_id}/{week}/radar_team_{idx+1:02d}.png"
        s3op.write_image_to_s3(img_data, radar_chart_file_path)
    update_status(task_id, { "state": 'IN PROGRESS', "percentage": 80 })

    # matchup forecast for next week
    next_matchup_charts = chart.next_matchup_radar_charts(total_score, next_matchup_arr, forecast_week)
    for idx, img_data in enumerate(next_matchup_charts):
        radar_chart_file_path = f"{season}/{league_id}/{week}/radar_forecast_{idx+1:02d}.png"
        s3op.write_image_to_s3(img_data, radar_chart_file_path)
    update_status(task_id, { "state": 'COMPLETED', "percentage": 100  })


def update_status(taskId, status):
    # Get the current timestamp
    now = int(datetime.now().timestamp())
    # Get the timestamp for a year later
    ttl = int((datetime.now() + timedelta(days=365)).timestamp())

    dynamodb = boto3.resource('dynamodb') 
    logger.debug('update task status to dynamodb table %s', os.environ.get("DB_TASK_TABLE"))
    table = dynamodb.Table(os.environ.get("DB_TASK_TABLE")) 
    #inserting values into table 

    response = table.update_item(
        Key={'taskId': taskId},
        UpdateExpression='SET #state=:val1, percentage=:val2, last_updated=:val3, expireAt=:val4',
        ExpressionAttributeNames={
            '#state': 'state'
        },
        ExpressionAttributeValues =json.loads(json.dumps({
            ':val1':  status['state'],
            ':val2':  status.get('percentage', 0),
            ':val3':  now,
            ':val4':  ttl
        })),
        ReturnValues="UPDATED_NEW"
    )
    logger.debug(response["Attributes"])