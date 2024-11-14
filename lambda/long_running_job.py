#!/usr/bin/env python
from datetime import datetime, timedelta
import boto3
import json
import os
import pandas as pd
import numpy as np

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
    update_status(task_id, { "state": 'IN_PROGRESS', "percentage": 1 })
   
    game_stat_categories = fapi.get_game_stat_categories()
    teams = fapi.get_league_teams(league_key, league_id)
    team_keys = list(map(lambda x: x['team_key'], teams))
    update_status(task_id, { "state": 'IN_PROGRESS', "percentage": 5 })

    total_df, sort_orders = fapi.get_league_stats(team_keys, game_stat_categories, 0)
    week_df, sort_orders  = fapi.get_league_stats(team_keys, game_stat_categories, week)
    update_status(task_id, { "state": 'IN_PROGRESS', "percentage": 10 })
    
    week_score = cmpt.stat_to_score(week_df, sort_orders)
    total_score = cmpt.stat_to_score(total_df, sort_orders)
    matchup_arr, matchup_dict = fapi.get_league_matchup(team_keys, week)
    battle_score = cmpt.roto_score_to_battle_score(week_score, matchup_dict)
    update_status(task_id, { "state": 'IN_PROGRESS', "percentage": 20 })

    season = utils.get_season()
    # write data frame to cvs on S3
    # total_stats_csv_file_key = f"{season}/{league_id}/0/stats.csv"
    # total_score_csv_file_key = f"{season}/{league_id}/0/roto-point.csv"
    # week_stats_csv_file_key = f"{season}/{league_id}/{week}/stats.csv"
    # week_score_csv_file_key = f"{season}/{league_id}/{week}/roto-point.csv"
    # week_battle_csv_file_key = f"{season}/{league_id}/{week}/h2h-score.csv"

    # s3op.write_dataframe_to_csv_on_s3(total_df, total_stats_csv_file_key)
    # s3op.write_dataframe_to_csv_on_s3(total_score, total_score_csv_file_key)
    # s3op.write_dataframe_to_csv_on_s3(week_df, week_stats_csv_file_key)
    # s3op.write_dataframe_to_csv_on_s3(week_score, week_score_csv_file_key)
    # s3op.write_dataframe_to_csv_on_s3(battle_score, week_battle_csv_file_key)

    # write data frame to excel on S3
    tier_point = total_df.shape[1]  / 2
    logger.debug(f"tier_point: {tier_point}")
    styled_battle_score = apply_style_for_h2h_df(battle_score, tier_point, f'H2H Matchup - Week {week}')
    styled_week_score = apply_style_for_roto_df(week_score, f'Roto Points - Week {week}')
    styled_week_stats = apply_style_for_roto_df(week_df, f'Stats - Week {week}')
    styled_total_score = apply_style_for_roto_df(total_score, 'Roto Points - Total')
    styled_total_stats = apply_style_for_roto_df(total_df, 'Stats - Total')

    # write to excel
    result_excel_file_key = f"{season}/{league_id}/{week}/{league_id}_{week}_result.xlsx"
    styled_dfs = [styled_battle_score, styled_week_score, styled_week_stats, styled_total_score, styled_total_stats]
    sheet_names = ['Matchup', 'Points - Week', 'Stats - Week', 'Points - Total', 'Stats - Total']
    s3op.write_styled_dataframe_to_excel_on_s3(styled_dfs, sheet_names, result_excel_file_key)

    # roto_point_week_table_file_path = f"{season}/{league_id}/{week}/roto_point_wk{week:02d}.png"
    # s3op.write_styled_dataframe_to_image_on_s3(styled_week_score, roto_point_week_table_file_path)

    # write to html
    roto_point_week_html_file_path = f"{season}/{league_id}/{week}/roto_point_wk{week:02d}.html"
    roto_stats_week_html_file_path = f"{season}/{league_id}/{week}/roto_stats_wk{week:02d}.html"
    roto_point_total_html_file_path = f"{season}/{league_id}/{week}/roto_point_total.html"
    roto_stats_total_html_file_path = f"{season}/{league_id}/{week}/roto_stats_total.html"
    h2h_matchup_week_html_file_path = f"{season}/{league_id}/{week}/h2h_matchup_wk{week:02d}.html"
    s3op.write_styled_dataframe_to_html_on_s3(styled_week_score, roto_point_week_html_file_path)
    s3op.write_styled_dataframe_to_html_on_s3(styled_week_stats, roto_stats_week_html_file_path)
    s3op.write_styled_dataframe_to_html_on_s3(styled_total_score, roto_point_total_html_file_path)
    s3op.write_styled_dataframe_to_html_on_s3(styled_total_stats, roto_stats_total_html_file_path)
    s3op.write_styled_dataframe_to_html_on_s3(styled_battle_score, h2h_matchup_week_html_file_path)
    update_status(task_id, { "state": 'IN_PROGRESS', "percentage": 25 })

    forecast_week = utils.get_forecast_week(league_id)
    next_matchup_arr, next_matchup_dict = fapi.get_league_matchup(team_keys, forecast_week)
    matchup_file_path = f"{season}/{league_id}/{forecast_week}/matchup.json"
    s3op.write_json_to_s3(next_matchup_arr, matchup_file_path)
    update_status(task_id, { "state": 'IN_PROGRESS', "percentage": 30 })

    league_name = utils.get_league_info(league_id)['name']
    week_bar_chart = chart.league_bar_chart(week_score, '{} 战力榜 - Week {}'.format(league_name, week))
    roto_week_bar_file_path = f"{season}/{league_id}/{week}/roto_bar_wk{week:02d}.png"
    s3op.write_image_to_s3(week_bar_chart, roto_week_bar_file_path)
    update_status(task_id, { "state": 'IN_PROGRESS', "percentage": 35 })

    total_bar_chart = chart.league_bar_chart(total_score, '{} 战力榜 - Total'.format(league_name))
    roto_total_bar_file_path = f"{season}/{league_id}/{week}/roto_bar_total.png"
    s3op.write_image_to_s3(total_bar_chart, roto_total_bar_file_path)
    update_status(task_id, { "state": 'IN_PROGRESS', "percentage": 40 })

    # radar chart for each team
    team_num = len(team_keys)
    step = 40 / team_num
    radar_charts = chart.league_radar_charts(week_score, total_score, week)
    for idx, img_data in enumerate(radar_charts):
        radar_chart_file_path = f"{season}/{league_id}/{week}/radar_team_{idx+1:02d}.png"
        s3op.write_image_to_s3(img_data, radar_chart_file_path)
        update_status(task_id, { "state": 'IN_PROGRESS', "percentage": int( (idx+1) * step + 40) })

    # matchup forecast for next week
    next_matchup_charts = chart.next_matchup_radar_charts(total_score, next_matchup_arr, forecast_week)
    for idx, img_data in enumerate(next_matchup_charts):
        radar_chart_file_path = f"{season}/{league_id}/{week}/radar_forecast_{idx+1:02d}.png"
        s3op.write_image_to_s3(img_data, radar_chart_file_path)
        update_status(task_id, { "state": 'IN_PROGRESS', "percentage": int( (idx+1) * step + 80) })
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



def highlight_max_min(s):
    """
    Highlight the maximum value in a Series with a green background
    and the minimum value with a red background.
    
    Parameters
    ----------
    s : pandas.Series
        The Series to be styled.
    
    Returns
    -------
    pandas.Series
        The styled Series with the maximum and minimum values highlighted.
    """

    # green background
    style_top = 'background-color: #C6EFCE; border: 2px dashed #006100'

    # red background
    style_bottom = 'background-color: #FFC7CE; border: 2px dashed #9C0006'

    is_max = s == s.max()
    is_min = s == s.min()
    return [style_top if v else style_bottom if m else '' for v, m in zip(is_max, is_min)]

def highlight_based_on_value(s, value):
    """
    Highlight values in a Series based on comparison with a given value.
    
    Parameters
    ----------
    s : pandas.Series
        The Series to be styled.
    value : float
        The value to compare against.
    
    Returns
    -------
    pandas.Series
        The styled Series with different background colors for values greater than,
        equal to, and less than the given value.
    """
    styles = []
    for v in s:
        if v == '' or v == 'nan' or pd.isna(v):
            styles.append('background-color: white; border: 1px solid black')
        elif v > value:
            styles.append('background-color: #C6EFCE; color: #006100')
        elif v == value:
            styles.append('background-color: #FFEB9C; color: #9C6500')
        else:
            styles.append('background-color: #FFC7CE; color: #9C0006')
    return styles

def highlight_last_three_columns(s):
    """
    Highlight the last three columns in a Series with a blue background.
    
    Parameters
    ----------
    s : pandas.Series
        The Series to be styled.
    
    Returns
    -------
    pandas.Series
        The styled Series with the last three columns highlighted.
    """
    return ['background-color: black; color: lawngreen; border-color: white' if i >= len(s) - 3 else '' for i in range(len(s))]


def remove_trailing_zeros(x):
    """
    Remove trailing zeros from a number.
    
    Parameters
    ----------
    x : float
        The number to be formatted.
    
    Returns
    -------
    str
        The formatted number as a string without trailing zeros.
    """
    value = x
    if x == 'nan' or pd.isna(x):
        value = ''
    elif isinstance(x, (float, np.float64)):
        value = ('%f' % x).rstrip('0').rstrip('.')
    return value


def apply_style_for_roto_df(df, caption):

    styled_df = df.style.apply(highlight_max_min, axis=0)\
        .format(remove_trailing_zeros)\
        .set_caption(caption)

    return styled_df

def apply_style_for_h2h_df(df, tier_point, caption):

    styled_df = df.style.apply(highlight_based_on_value, value=tier_point, subset=df.columns[0:-3])\
        .apply(highlight_last_three_columns, subset=df.columns[-3:], axis=1)\
        .format(remove_trailing_zeros)\
        .set_caption(caption)

    return styled_df
