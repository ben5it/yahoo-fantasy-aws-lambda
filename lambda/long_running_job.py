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
    task_id = utils.get_task_id(league_id, week)
    update_task_status(task_id, { "state": 'IN_PROGRESS', "percentage": 1 })

    # remove all previous analysis result
    season = utils.get_season()
    folder_key = f"{season}/{league_id}/{week}/"
    s3op.remove_all_files_in_folder_in_s3(folder_key)

    # get stats of all teams for the total season
    league_info = utils.get_league_info(league_id)
    league_key = league_info['league_key']
    teams = fapi.get_league_teams(league_key, league_id)
    team_keys = list(map(lambda x: x['team_key'], teams))
    team_ids = list(map(lambda x: int(x['team_id']), teams))
    game_stat_categories = fapi.get_game_stat_categories()
    total_stats_df, sort_orders = fapi.get_league_stats(team_keys, game_stat_categories, 0)
    update_task_status(task_id, {  "percentage": 5 })

    # get matchup data of this week, which includes team stats and matchup info
    week_info, week_stats_df, week_score_df = fapi.get_league_matchup(teams, week, game_stat_categories)
    week_status = week_info['status']
    week_info_file_path = f"{season}/{league_id}/{week}/week_info.json"
    s3op.write_json_to_s3(week_info, week_info_file_path)
    week_score_file_path = f"{season}/{league_id}/{week}/week_score.csv"
    s3op.write_dataframe_to_csv_on_s3(week_score_df, week_score_file_path)
    update_task_status(task_id, {  "percentage": 10, "week_status": week_status })
    
    week_score_df = cmpt.stat_to_score(week_stats_df, sort_orders)
    total_score_df = cmpt.stat_to_score(total_stats_df, sort_orders)
    battle_score_df = cmpt.roto_score_to_battle_score(week_score_df, week_info['matchups'])
    update_task_status(task_id, {  "percentage": 15 })

    # write data frame to excel on S3
    tier_point = total_stats_df.shape[1]  / 2
    logger.debug(f"tier_point: {tier_point}")
    styled_battle_score = apply_style_for_h2h_df(battle_score_df, tier_point, f'H2H Matchup - Week {week}')
    styled_week_score = apply_style_for_roto_df(week_score_df, f'Roto Points - Week {week}')
    styled_week_stats = apply_style_for_roto_df(week_stats_df, f'Stats - Week {week}')
    styled_total_score = apply_style_for_roto_df(total_score_df, 'Roto Points - Total')
    styled_total_stats = apply_style_for_roto_df(total_stats_df, 'Stats - Total')
    update_task_status(task_id, {  "percentage": 20 })

    # write to excel
    result_excel_file_key = f"{season}/{league_id}/{week}/{league_id}_{week}_result.xlsx"
    styled_dfs = [styled_battle_score, styled_week_score, styled_week_stats, styled_total_score, styled_total_stats]
    sheet_names = ['Matchup', 'Points - Week', 'Stats - Week', 'Points - Total', 'Stats - Total']
    s3op.write_styled_dataframe_to_excel_on_s3(styled_dfs, sheet_names, result_excel_file_key)
    update_task_status(task_id, {  "percentage": 25 })

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
    s3op.write_styled_dataframe_to_html_on_s3(styled_battle_score, h2h_matchup_week_html_file_path, False)
    update_task_status(task_id, {  "percentage": 30 })

    # bar chart for week roto score
    league_name = utils.get_league_info(league_id)['name']
    week_bar_chart = chart.league_bar_chart(week_score_df, '{} 战力榜 - Week {}'.format(league_name, week))
    roto_week_bar_file_path = f"{season}/{league_id}/{week}/roto_bar_wk{week:02d}.png"
    s3op.write_image_to_s3(week_bar_chart, roto_week_bar_file_path)
    update_task_status(task_id, {  "percentage": 35 })

    # bar chart for total roto score
    total_bar_chart = chart.league_bar_chart(total_score_df, '{} 战力榜 - Total'.format(league_name))
    roto_total_bar_file_path = f"{season}/{league_id}/{week}/roto_bar_total.png"
    s3op.write_image_to_s3(total_bar_chart, roto_total_bar_file_path)
    update_task_status(task_id, {  "percentage": 40 })

    # radar chart for each team
    start_progress = 40
    end_progress = 80
    step = (end_progress - start_progress) / len(teams)
    stat_names = week_score_df.columns.values.tolist()[:-1] # get the stat names, need to remove the last column 'total'
    team_names = week_score_df.index.tolist()
    for idx, team_name in enumerate(team_names):
        # get the stat scores, need to remove the last column 'total'
        week_score = week_score_df.loc[team_name].values.tolist()[:-1]
        total_score = total_score_df.loc[team_name].values.tolist()[:-1]
        img_data = chart.get_radar_chart(stat_names, [total_score, week_score], len(team_names), ['Total', 'Week {}'.format(week)], team_name)
        radar_chart_file_path = f"{season}/{league_id}/{week}/radar_team_{idx+1:02d}.png"
        s3op.write_image_to_s3(img_data, radar_chart_file_path)
        percentage = int(start_progress + step * (idx + 1))
        update_task_status(task_id, {  "percentage": percentage })


    # matchup forecast for next week
    forecast_week = utils.get_forecast_week(league_id)
    if forecast_week > week:
        week_info, week_stats_df, team_score_df = fapi.get_league_matchup(teams, forecast_week, game_stat_categories)
        week_info_file_path = f"{season}/{league_id}/{forecast_week}/week_info.json"
        s3op.write_json_to_s3(week_info, week_info_file_path)


    # get the stat names, need to remove the last column 'total'
    stat_names = total_score_df.columns.values.tolist()[:-1]
    team_names = total_score_df.index.tolist()
    chart_title = '第{}周对战参考'.format(forecast_week)
    matchups = week_info['matchups']
    start_progress = 80
    end_progress = 100
    step = (end_progress - start_progress) / len(matchups)

    # generate radar chart for each matchup next week
    for idx in range(0, len(matchups), 2 ): 
        team_name_1 = matchups[idx]
        team_name_2 = matchups[idx+1]
        labels = [team_name_1,  team_name_2]
        team_score_1 = total_score_df.loc[team_name_1].values.tolist()[:-1]
        team_score_2 = total_score_df.loc[team_name_2].values.tolist()[:-1]
        img_data = chart.get_radar_chart(stat_names, [team_score_1, team_score_2], len(team_names), labels, chart_title)
        radar_chart_file_path = f"{season}/{league_id}/{week}/radar_forecast_{idx+1:02d}.png"
        s3op.write_image_to_s3(img_data, radar_chart_file_path)
        percentage = int(start_progress + step * (idx + 2))
        update_task_status(task_id, {  "percentage": percentage })


    # calculate the cumulative score
    start_week = int(league_info['start_week'])
    end_week = league_info['current_week']
    # only calculate when there are at least two post event weeks
    if end_week > start_week + 1:
        has_missing_data = False
        selected_columns = ['Win', 'Point' ]
        # Create a new DataFrame with the same index and columns as week_score_df, but with all values set to zero
        cumulative_score_df = pd.DataFrame(0, index=week_score_df.index, columns=selected_columns)
        # Add new columns 'Previous_Point' and 'Previous_Win' with value 0
        cumulative_score_df['Previous_Point'] = team_ids
        cumulative_score_df['Previous_Win'] = 0

        cumulative_rank_df = pd.DataFrame(index=week_score_df.index)

        for i in range(start_week, end_week):   
            this_week_score_file_path = f"{season}/{league_id}/{i}/week_score.csv"
            this_week_score_df = s3op.load_dataframe_from_csv_on_s3(this_week_score_file_path)
            # logger.info(this_week_score_df)
            if this_week_score_df is None:
                has_missing_data = True
                logger.debug(f"Cannot calculate cumulative score because week score data for league {league_id} week {i} is missing")
                break  # no need to continue if one week data is missing

            week_selected = this_week_score_df[selected_columns]
            # Add the selected columns element-wise
            cumulative_score_df = cumulative_score_df.add(week_selected, fill_value=0)
            # logger.info(cumulative_score_df)
            cumulative_rank_df[f'week {i}'] = cumulative_score_df[['Point', 'Win', 'Previous_Point', 'Previous_Win']].apply(tuple, axis=1).rank(method='min', ascending=False).astype(int)
            # logger.info(cumulative_rank_df)

            # Update the 'Previous_Point' and 'Previous_Win' columns for next iteration to compute the rank
            cumulative_score_df['Previous_Point'] = cumulative_score_df['Point']
            cumulative_score_df['Previous_Win'] = cumulative_score_df['Win']

        if not has_missing_data:
            # write to csv
            cumulative_rank_file_path = f"{season}/{league_id}/{week}/cumulative_rank.csv"
            s3op.write_dataframe_to_csv_on_s3(cumulative_rank_df, cumulative_rank_file_path)

    update_task_status(task_id, { "state": 'COMPLETED', "percentage": 100  })


def update_task_status(taskId, status):
    # Get the current timestamp
    now = int(datetime.now().timestamp())
    # Get the timestamp for a year later
    ttl = int((datetime.now() + timedelta(days=365)).timestamp())

    dynamodb = boto3.resource('dynamodb') 
    logger.debug('update task status to dynamodb table %s', os.environ.get("DB_TASK_TABLE"))
    table = dynamodb.Table(os.environ.get("DB_TASK_TABLE")) 
    #inserting values into table 

    expression_str = 'SET last_updated=:val1, expireAt=:val2'
    attribute_names = {}
    attribute_values = {
        ':val1':  now,
        ':val2':  ttl
    }

    if 'state' in status:
        expression_str += ', #state=:val3'
        attribute_values[':val3'] = status['state']
        attribute_names['#state'] = 'state'
    if 'percentage' in status:
        expression_str += ', percentage=:val4'
        attribute_values[':val4'] = status['percentage']
    if 'week_status' in status:
        expression_str += ', week_status=:val5'
        attribute_values[':val5'] = status['week_status']

    params = {
        'Key': {'taskId': taskId},
        'UpdateExpression': expression_str,
        'ExpressionAttributeValues' : json.loads(json.dumps(attribute_values)),
        'ReturnValues': "UPDATED_NEW"      
    }

    # Add ExpressionAttributeNames only if attribute_names is not empty
    if attribute_names:
        params['ExpressionAttributeNames'] = attribute_names

    response = table.update_item(**params)
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
    return ['background-color: black; color: lawngreen; border-color: black' if i >= len(s) - 3 else '' for i in range(len(s))]


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
