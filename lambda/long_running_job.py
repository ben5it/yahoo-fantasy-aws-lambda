#!/usr/bin/env python
from datetime import datetime, timedelta
import boto3
import gc
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

    # remove all exsiting analysis result for this week and season
    season = utils.get_season()
    week_folder_key = f"{season}/{league_id}/{week}/"
    s3op.remove_all_files_in_folder_in_s3(week_folder_key)
    season_folder_key = f"{season}/{league_id}/season/"
    # s3op.remove_all_files_in_folder_in_s3(season_folder_key)
    
    # we will first do analysis for this single week, 
    # then we do analysis for the whole season,
    # and then we do the cumulative analysis for the whole season
    # and finally we do the forecast for the next week

    # First step, retrieve data from Yahoo API
    league_info = utils.get_league_info(league_id)
    league_key = league_info['league_key']
    league_name = league_info['name']
    teams = fapi.get_league_teams(league_key, league_id)
    team_keys = list(map(lambda x: x['team_key'], teams))
    team_ids = list(map(lambda x: int(x['team_id']), teams))
    team_names = list(map(lambda x: x['name'], teams))
    game_stat_categories = fapi.get_game_stat_categories()
    # get stats of all teams for the total season
    total_stats_df, sort_orders = fapi.get_league_stats(team_keys, game_stat_categories, 0)
    stat_names = total_stats_df.columns.values.tolist()
    # get matchup data of this week, which includes team stats and matchup info
    week_info, week_stats_df, week_score_df = fapi.get_league_matchup(teams, week, game_stat_categories)
    week_status = week_info['status']
    update_task_status(task_id, {  "percentage": 5, "week_status": week_status })

    # ======================== Now start analysis for this single week ========================

    # write retrived data to s3
    week_info_file_path = week_folder_key + "week_info.json"
    s3op.write_json_to_s3(week_info, week_info_file_path)
    week_score_file_path = week_folder_key + "week_score.csv"
    s3op.write_dataframe_to_csv_on_s3(week_score_df, week_score_file_path)

    # output raw stats to s3
    roto_stats_week_html_file_path = week_folder_key + f"roto_stats.html"
    styled_week_stats = apply_style_for_roto_df(week_stats_df, f'Stats - Week {week}')
    s3op.write_styled_dataframe_to_html_on_s3(styled_week_stats, roto_stats_week_html_file_path)

    # calculate the roto point based on stats
    week_point_df = cmpt.stat_to_score(week_stats_df, sort_orders)
    week_point_csv_file_key = week_folder_key + "roto_point.csv"
    s3op.write_dataframe_to_csv_on_s3(week_point_df, week_point_csv_file_key)

    # generate bar chart for week total roto point
    week_bar_chart = chart.league_bar_chart(week_point_df, '{}第{}周战力榜'.format(league_name, week))
    roto_week_bar_file_path = week_folder_key + f"roto_bar.png"
    s3op.write_image_to_s3(week_bar_chart, roto_week_bar_file_path)

    # output detailed (With Categories) roto points to s3 as html table
    roto_point_week_html_file_path = week_folder_key + f"roto_point.html"
    styled_week_point = apply_style_for_roto_df(week_point_df, f'Points by Categories - Week {week}')
    s3op.write_styled_dataframe_to_html_on_s3(styled_week_point, roto_point_week_html_file_path)
    update_task_status(task_id, {  "percentage": 10 })

    # generate radar chart for each team for this week
    start_progress = 10
    end_progress = 25
    step = (end_progress - start_progress) / len(team_names)
    for idx, team_name in enumerate(team_names):
        # get the stat scores, need to remove the last column 'total'
        week_score = week_point_df.loc[team_name].values.tolist()[:-1]
        img_data = chart.get_radar_chart(stat_names, [ week_score], len(team_names), ['Week {}'.format(week)], team_name)
        radar_chart_file_path = week_folder_key + f"radar_team_{idx+1:02d}.png"
        s3op.write_image_to_s3(img_data, radar_chart_file_path)
        percentage = int(start_progress + step * (idx + 1))
        update_task_status(task_id, {  "percentage": percentage })

    # calculate the scores for assumed matchups with all other teams based on roto point
    matchup_score_df = cmpt.roto_score_to_battle_score(week_point_df, week_info['matchups'])
    matchup_csv_file_key = week_folder_key + "matchup_score.csv"
    s3op.write_dataframe_to_csv_on_s3(matchup_score_df, matchup_csv_file_key)

    # output matchup scores to s3 as html table
    tier_point = total_stats_df.shape[1]  / 2
    logger.debug(f"tier_point: {tier_point}")
    styled_matchup_score = apply_style_for_h2h_df(matchup_score_df, tier_point, f'Assumed Matchup - Week {week}')
    h2h_matchup_week_html_file_path = week_folder_key + f"matchup_score.html"
    s3op.write_styled_dataframe_to_html_on_s3(styled_matchup_score, h2h_matchup_week_html_file_path, False)

    # release memory
    del week_score_df, week_stats_df, styled_week_stats, week_point_df, styled_week_point, matchup_score_df, styled_matchup_score
    gc.collect()

    # ======================== Now start analysis for the whole season ========================

    # output season raw stats to s3
    styled_total_stats = apply_style_for_roto_df(total_stats_df, 'Stats - Total')
    roto_stats_total_html_file_path = season_folder_key + "roto_stats.html"
    s3op.write_styled_dataframe_to_html_on_s3(styled_total_stats, roto_stats_total_html_file_path)

    # calculate the roto point based on seanson stats
    total_point_df = cmpt.stat_to_score(total_stats_df, sort_orders)
    total_point_csv_file_key = season_folder_key + "total_point.csv"
    s3op.write_dataframe_to_csv_on_s3(total_point_df, total_point_csv_file_key)

    # bar chart for season roto score
    total_bar_chart = chart.league_bar_chart(total_point_df, '{}赛季总战力榜'.format(league_name))
    roto_total_bar_file_path = season_folder_key + "roto_bar.png"
    s3op.write_image_to_s3(total_bar_chart, roto_total_bar_file_path)

    # write detailed points by category to html table
    styled_total_point = apply_style_for_roto_df(total_point_df, 'Points by Categories - Total')
    roto_point_total_html_file_path = season_folder_key + "roto_point.html"
    s3op.write_styled_dataframe_to_html_on_s3(styled_total_point, roto_point_total_html_file_path)
    update_task_status(task_id, {  "percentage": 30 })

    # generate radar chart for each team for whole season
    start_progress = 30
    end_progress = 45
    step = (end_progress - start_progress) / len(teams)
    for idx, team_name in enumerate(team_names):
        # get the stat scores, need to remove the last column 'total'
        total_score = total_point_df.loc[team_name].values.tolist()[:-1]
        img_data = chart.get_radar_chart(stat_names, [total_score], len(team_names), ['Total'], team_name)
        radar_chart_file_path = season_folder_key + f"radar_team_{idx+1:02d}.png"
        s3op.write_image_to_s3(img_data, radar_chart_file_path)
        percentage = int(start_progress + step * (idx + 1))
        update_task_status(task_id, {  "percentage": percentage })

    # write to excel: don't neede to do this now
    # result_excel_file_key = week_folder_key + "{league_id}_{week}_result.xlsx"
    # styled_dfs = [styled_battle_score, styled_week_point, styled_week_stats, styled_total_point, styled_total_stats]
    # sheet_names = ['Matchup', 'Points - Week', 'Stats - Week', 'Points - Total', 'Stats - Total']
    # s3op.write_styled_dataframe_to_excel_on_s3(styled_dfs, sheet_names, result_excel_file_key)

    # release memory: total_point_df is used in the next step so not deleted here
    del total_stats_df, styled_total_stats, styled_total_point
    gc.collect()


    # ======================== Now start analysis for cumulative weeks ========================

    # only calculate when there are at least two post event weeks,
    # and the week to be analyzed is latest week can be analyzed
    start_week = int(league_info['start_week'])
    end_week = league_info['current_week']
    default_week = utils.get_default_week(league_id)
    if end_week > start_week + 1 and week == default_week:

        # will will output
        #  - ranks by week, 
        #  - total roto point by week
        #  - scores gained by each week
        #  - diff with assumed matchup median score by week
        #  - openent's rank diff of this week with total

        # flag to indicate if there is missing data for any week, if so we cannot canculate cumulative data
        has_missing_data = False

        # add a rank column to the total point dataframe, will use this to calculate the rank diff between a week and total
        total_point_df['Rank'] = total_point_df[['Total']].apply(tuple, axis=1).rank(method='min', ascending=False).astype(int)

        # start calculating standing by week, there is no existing data so that we need to calculate from week 1
        # by adding the win, tie, and lose columns element-wise

        cumulative_score_by_category_df = pd.DataFrame(0, index=team_names, columns=stat_names)

        rank_trend_df = pd.DataFrame(index=team_names)
        point_trend_df = pd.DataFrame(index=team_names)
        score_trend_df = pd.DataFrame(index=team_names)

        # Below two dataframes are used to calculate the luck index for each team
        # Luck in H2H means you meet the right opponent at the right time
        #   - diff_from_median_over_weeks_df: 
        #           this indicates whether you meet the right opponent.
        #           say this week your matchup score is 7:4 with your opponent, then you get 7 this week.
        #           If there are 18 teams in your leagues, we will calcualte the virtual matchup score between you and all
        #           the other teams, and get the median you can get. Then we can get the difference between you actual score and median
        #   - diff_from_total_over_weeks_df
        #           This indicates whether you meet your opponent at the right time.
        #           say your current opponent ranks the 1 in total, but this week he only ranks the 5, then you get -4 this week
        #           this dataframe will store this data for each team for each week

        diff_from_median_over_weeks_df = pd.DataFrame(index=team_names)
        diff_from_total_over_weeks_df  = pd.DataFrame(index=team_names)


        start_progress = 45
        end_progress = 55
        step = (end_progress - start_progress) / (end_week - start_week)

        for i in range(start_week, end_week):   
            this_week_score_file_path = f"{season}/{league_id}/{i}/week_score.csv"
            this_week_score_df = s3op.load_dataframe_from_csv_on_s3(this_week_score_file_path)

            this_week_point_file_path = f"{season}/{league_id}/{i}/roto_point.csv"
            this_week_point_df = s3op.load_dataframe_from_csv_on_s3(this_week_point_file_path)

            this_week_matchup_file_path = f"{season}/{league_id}/{i}/matchup_score.csv"
            this_week_matchup_df = s3op.load_dataframe_from_csv_on_s3(this_week_matchup_file_path)

            this_week_info_file_path = f"{season}/{league_id}/{i}/week_info.json"
            this_week_info_json, this_week_info_last_modified = s3op.load_json_from_s3(this_week_info_file_path)
            
            if (this_week_score_df is None or 
                this_week_matchup_df is None or 
                this_week_point_df is None or 
                this_week_info_json is None):

                has_missing_data = True
                logger.debug(f"Cannot calculate cumulative data for league {league_id} because week {i} data is missing")
                break  # no need to continue if one week data is missing

            # Add the selected columns element-wise
            cumulative_score_by_category_df = cumulative_score_by_category_df.add(this_week_score_df, fill_value=0)

            # calculate the rank based on the total point. For tie break, use the previous week's point
            # If there's still a tie, the process continues for each previous week.
            # If the process reaches the first week and there is still a tie, the team with more 'win' wins.
            # If there is still a tie, the team with the lower team ID wins.
            # so add the week point and win columns for each week for sorting, we will remove them later after sorting
            cumulative_score_by_category_df[f'Point_week_{i}'] = this_week_score_df['Point']
            if i == start_week:
                cumulative_score_by_category_df[f'Win_week_{i}'] = this_week_score_df['Win']
                cumulative_score_by_category_df['team_ids'] = team_ids

            columns_for_sort = ['Point']  # This is the total point column
            # Loop from i to start_week by decreasing i
            for j in range(i, start_week - 1, -1):
                columns_for_sort.append(f'Point_week_{j}')
            columns_for_sort.append(f'Win_week_{start_week}')
            columns_for_sort.append('team_ids') # for the first week, if point and win are the same, sort by team id

            # calculate current rank at a specific week
            cumulative_score_by_category_df['Rank'] = cumulative_score_by_category_df[columns_for_sort].apply(tuple, axis=1).rank(method='min', ascending=False).astype(int)

            # Add the rank column for each week to the rank_trend_df
            rank_trend_df[f'week {i}'] = cumulative_score_by_category_df['Rank']
            point_trend_df[f'week {i}'] = this_week_point_df['Total']
            score_trend_df[f'week {i}'] = this_week_score_df['Point']
            diff_from_median_over_weeks_df[f'week {i}'] = this_week_matchup_df['分差']

            # calculate the rank diff from total rank
            diff_from_total_over_weeks_df[f'week {i}'] = 0
            this_week_point_df['Rank'] = this_week_point_df[['Total']].apply(tuple, axis=1).rank(method='min', ascending=False).astype(int)
            this_week_matchup_array = this_week_info_json['matchups']
            for idx in range(0, len(this_week_matchup_array), 2 ): 
                team_name_1 = this_week_matchup_array[idx]
                team_name_2 = this_week_matchup_array[idx+1]
                team_1_total_rank = total_point_df.loc[team_name_1]['Rank']
                team_2_total_rank = total_point_df.loc[team_name_2]['Rank']
                team_1_week_rank = this_week_point_df.loc[team_name_1]['Rank']
                team_2_week_rank = this_week_point_df.loc[team_name_2]['Rank']
                team_1_diff = team_1_week_rank - team_1_total_rank
                team_2_diff = team_2_week_rank - team_2_total_rank
                diff_from_total_over_weeks_df.at[team_name_1, f'week {i}'] = team_2_diff
                diff_from_total_over_weeks_df.at[team_name_2, f'week {i}'] = team_1_diff

            percentage = int(start_progress + step * (i + 1))
            update_task_status(task_id, {  "percentage": percentage })

        if not has_missing_data:

            # generate rank chrt for cumulative weeks
            rank_trend_img_file_path = season_folder_key + "rank_trend.png"
            img_data = chart.generate_rank_chart(rank_trend_df, league_name)
            s3op.write_image_to_s3(img_data, rank_trend_img_file_path)

            # generate point chart for cumulative weeks
            point_trend_img_file_path = season_folder_key + "point_trend.png"
            img_data = chart.generate_line_chart(point_trend_df, '每周战力', 'Point', league_name)
            s3op.write_image_to_s3(img_data, point_trend_img_file_path)

            # generate score chart for cumulative weeks
            score_trend_img_file_path = season_folder_key + "score_trend.png"
            img_data = chart.generate_line_chart(score_trend_df, '每周得分', 'Score', league_name)
            s3op.write_image_to_s3(img_data, score_trend_img_file_path)

            # add a column to display the total score of each team (row)
            diff_from_median_over_weeks_df['Total'] = diff_from_median_over_weeks_df.sum(axis=1)
            styled_diff_from_median_over_weeks_df = diff_from_median_over_weeks_df.style\
                .apply(highlight_max_min, axis=0)\
                .format(remove_trailing_zeros)\
                .set_caption('要是打XXX，我就赢了')
            cumulative_matchup_html_file_path = season_folder_key + "median_diff_trend.html"
            s3op.write_styled_dataframe_to_html_on_s3(styled_diff_from_median_over_weeks_df, cumulative_matchup_html_file_path)


            # add a column to display the total score of each team (row)
            diff_from_total_over_weeks_df['Total'] = diff_from_total_over_weeks_df.sum(axis=1)
            styled_diff_from_total_over_weeks_df = diff_from_total_over_weeks_df.style\
                .apply(highlight_max_min, axis=0)\
                .format(remove_trailing_zeros)\
                .set_caption('我去，我对手这周怎么这么爆')
            total_diff_trend_html_file_path = season_folder_key + "total_diff_trend.html"
            s3op.write_styled_dataframe_to_html_on_s3(styled_diff_from_total_over_weeks_df, total_diff_trend_html_file_path)


            # Convert 'Win', 'Lose', and 'Tie' columns to strings and create 'W-L-T' column
            cumulative_score_by_category_df['W-L-T'] = (
                cumulative_score_by_category_df['Win'].astype(int).astype(str) + '-' +
                cumulative_score_by_category_df['Lose'].astype(int).astype(str) + '-' +
                cumulative_score_by_category_df['Tie'].astype(int).astype(str)
            )
  
            # Drop some intermidiate columns and only keep the stat columns, 'W-L-T', and 'Rank'
            desired_column_names = stat_names + ['W-L-T', 'Rank']
            cumulative_score_by_category_df = cumulative_score_by_category_df[desired_column_names]
            cumulative_score_by_category_df = cumulative_score_by_category_df.sort_values(by=['Rank'], ascending=True)
            styled_cumulative_score_by_category_df = cumulative_score_by_category_df.style\
                .apply(highlight_max_min, subset=cumulative_score_by_category_df.columns[0:-2], axis=0)\
                .format(remove_trailing_zeros)\
                .set_caption('Score by category')
            cumulative_score_html_file_path = season_folder_key + "standing.html"
            s3op.write_styled_dataframe_to_html_on_s3(styled_cumulative_score_by_category_df, cumulative_score_html_file_path)

            update_task_status(task_id, {  "percentage": 60 })

            # generate pie chart for each team
            start_progress = 60
            end_progress = 75
            step = (end_progress - start_progress) / len(team_names)
            cumulative_score_by_category_df = cumulative_score_by_category_df[stat_names]
            for idx, team_name in enumerate( cumulative_score_by_category_df.index):
                img_data = chart.generate_category_pie_chart_for_team(cumulative_score_by_category_df, team_name)
                pie_chart_file_path = season_folder_key + f"pie_chart_{idx+1:02d}.png"
                s3op.write_image_to_s3(img_data, pie_chart_file_path)
                percentage = int(start_progress + step * (idx + 1))
                update_task_status(task_id, {  "percentage": percentage })

        del cumulative_score_by_category_df, \
            styled_cumulative_score_by_category_df,\
            rank_trend_df, \
            point_trend_df, \
            score_trend_df, \
            diff_from_median_over_weeks_df, \
            diff_from_total_over_weeks_df, \
            styled_diff_from_median_over_weeks_df, \
            styled_diff_from_total_over_weeks_df
        gc.collect()
    update_task_status(task_id, {  "percentage": 75 })

    # ======================== Now start analysis for forecast ========================

    # matchup forecast for next week
    forecast_week = utils.get_forecast_week(league_id)
    if forecast_week > week:
        week_info, week_stats_df, team_score_df = fapi.get_league_matchup(teams, forecast_week, game_stat_categories)
        week_info_file_path = f"{season}/{league_id}/{forecast_week}/week_info.json"
        s3op.write_json_to_s3(week_info, week_info_file_path)
    update_task_status(task_id, {  "percentage": 80 })

    chart_title = '第{}周对战参考'.format(forecast_week)
    matchups = week_info['matchups']
    start_progress = 80
    end_progress = 95
    step = (end_progress - start_progress) / len(matchups)
    total_point_df = total_point_df[stat_names]
    # generate radar chart for each matchup next week
    for idx in range(0, len(matchups), 2 ): 
        team_name_1 = matchups[idx]
        team_name_2 = matchups[idx+1]
        labels = [team_name_1,  team_name_2]
        team_score_1 = total_point_df.loc[team_name_1].values.tolist()
        team_score_2 = total_point_df.loc[team_name_2].values.tolist()
        img_data = chart.get_radar_chart(stat_names, [team_score_1, team_score_2], len(team_names), labels, chart_title)
        radar_chart_file_path = season_folder_key + f"radar_forecast_{int(idx/2+1):02d}.png"
        s3op.write_image_to_s3(img_data, radar_chart_file_path)
        percentage = int(start_progress + step * (idx + 2))
        update_task_status(task_id, {  "percentage": percentage })

    # comes to the end
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

def highlight_last_n_columns(s, n):
    """
    Highlight the last n columns in a Series with a blue background.
    
    Parameters
    ----------
    s : pandas.Series
        The Series to be styled.
    
    Returns
    -------
    pandas.Series
        The styled Series with the last n columns highlighted.
    """
    return ['background-color: black; color: lawngreen; border-color: black' if i >= len(s) - n else '' for i in range(len(s))]


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
        .apply(highlight_last_n_columns, n=3, subset=df.columns[-3:], axis=1)\
        .format(remove_trailing_zeros)\
        .set_caption(caption)

    return styled_df
