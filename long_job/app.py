#!/usr/bin/env python


import shared.config as logger
import shared.s3_operation as s3op
import shared.utils as utils
import shared.fantasy_api as fapi

import chart as chart
import compute as cmpt
import fantasy_api as fapi

def lambda_handler(event, context):

    logger.debug(event)

    if 'sessionId' not in body:
        logger.error('Invalid input: sessionId is missing')


    sessionId = event['sessionId']
    valid, access_token = utils.is_valid_session(sessionId)
    if valid == False:
        logger.error('Invalid session')

    fapi.set_access_token(access_token)

    if 'league_key' not in body or 'league_id' not in body or 'week' not in body :
        logger.error('Invalid input: league_key, league_id or week is missing')

    league_key = event['league_key']
    league_id = event['league_id']
    week = int(event['week'])

    task_id = utils.get_task_id(league_id, week)
    update_status(task_id, { status: 'IN PROGRESS', percentage: 0 })
   
    game_stat_categories = fapi.get_game_stat_categories()
    teams = fapi.get_league_teams(league_key, league_id)
    team_keys = list(map(lambda x: x['team_key'], teams))
    update_status(task_id, { status: 'IN PROGRESS', percentage: 5 })

    total_df, sort_orders, points = fapi.get_league_stats(team_keys, game_stat_categories, 0)
    week_df, sort_orders, week_points = fapi.get_league_stats(team_keys, game_stat_categories, week)
    update_status(task_id, { status: 'IN PROGRESS', percentage: 15 })
    
    week_score = cmpt.stat_to_score(week_df, sort_orders)
    total_score = cmpt.stat_to_score(total_df, sort_orders)
    battle_score = cmpt.roto_score_to_battle_score(week_score, week_points)
    update_status(task_id, { status: 'IN PROGRESS', percentage: 25 })

    # write to S3
    season = utils.get_season()
    total_stats_csv_file_key = f"data/{season}/{league_id}/0/stats.csv"
    total_score_csv_file_key = f"data/{season}/{league_id}/0/roto-score.csv"
    week_stats_csv_file_key = f"data/{season}/{league_id}/{week}/stats.csv"
    week_score_csv_file_key = f"data/{season}/{league_id}/{week}/roto-score.csv"
    week_battle_csv_file_key = f"data/{season}/{league_id}/{week}/battle-score.csv"

    s3op.write_dataframe_to_csv_on_s3(total_df, total_stats_csv_file_key)
    s3op.write_dataframe_to_csv_on_s3(total_score, total_score_csv_file_key)
    s3op.write_dataframe_to_csv_on_s3(week_df, week_stats_csv_file_key)
    s3op.write_dataframe_to_csv_on_s3(week_score, week_score_csv_file_key)
    s3op.write_dataframe_to_csv_on_s3(battle_score, week_battle_csv_file_key)
    update_status(task_id, { status: 'IN PROGRESS', percentage: 40 })

    predict_week = utils.get_prediction_week(league_id)
    next_matchups = fapi.get_league_matchup(team_keys, predict_week)
    # matchup_file_path = f"data/{season}/{league_id}/{week}/matchup.json"
    # s3op.write_json_to_s3(matchup_file_path)
    update_status(task_id, { status: 'IN PROGRESS', percentage: 50 })

    # week_bar_chart = chart.league_bar_chart(week_score, '{} 战力榜 - Week {}'.format(league_name, week))
    # total_bar_chart = chart.league_bar_chart(total_score, '{} 战力榜 - Total'.format(league_name))
    update_status(task_id, { status: 'IN PROGRESS', percentage: 60 })

    # radar chart for each team
    radar_charts = chart.league_radar_charts(week_score, total_score, week)
    for idx, img_data in enumerate(radar_charts):
        radar_chart_file_path = f"data/{season}/{league_id}/{week}/chart/r_d_{idx:02d}.png"
        s3op.write_image_to_s3(img_data, radar_chart_file_path)
    update_status(task_id, { status: 'IN PROGRESS', percentage: 80 })

    # matchup prediction for next week
    next_matchup_charts = chart.next_matchup_radar_charts(total_score, next_matchups, predict_week)
    for idx, img_data in enumerate(next_matchup_charts):
        radar_chart_file_path = f"data/{season}/{league_id}/{week}/chart/r_c_{idx:02d}.png"
        s3op.write_image_to_s3(img_data, radar_chart_file_path)
    update_status(task_id, { status: 'COMPLETED' })


 def update_status(taskId, status):

    pass