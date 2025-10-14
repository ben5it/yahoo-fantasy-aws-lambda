#!/usr/bin/env python

import json
import objectpath
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone

import config as cfg
import s3_operation as s3op
import utils

logger = cfg.logger


ACCESS_TOKEN = ''

def set_access_token(token):
    global ACCESS_TOKEN
    ACCESS_TOKEN = token

def get_leagues():
    '''
    Return all leagues of current user for the recent season
    '''
    season = utils.get_season()
    logger.debug('get leagues for season {}'.format(season))

    uri = 'users;use_login=1/games;game_codes=nba;seasons={}/leagues'.format(season)
    resp = make_request(uri)
    logger.debug(json.dumps(resp))
    t = objectpath.Tree(resp)
    jfilter = t.execute('$..leagues..(league_key, league_id, name, url, logo_url, draft_status, num_teams, scoring_type, start_date, end_date, current_week, start_week, end_week)')

    leagues = []
    for l in jfilter:
        leagues.append(l)

    # sort by league id
    leagues.sort(key = lambda league : int(league['league_id']))

    logger.debug(json.dumps(leagues))
    # [{"league_key": "428.l.7124", "league_id": "7124", "name": "Never Ending", "logo_url": false, "scoring_type": "head", "start_date": "2023-10-24", "end_date": "2024-04-14", "current_week": 24, "start_week": "1", "end_week": "24"}, {"league_key": "428.l.23476", "league_id": "23476", "name": "2023~2024 Gamma", "logo_url": "https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/88a86479d6cf4bc472623e59484ab6c70e397336290032a9c744125e158d2c21.jpg", "scoring_type": "head", "start_date": "2023-10-24", "end_date": "2024-04-14", "current_week": 24, "start_week": "1", "end_week": "24"}]

    for league in leagues:
        league_id = league["league_id"]
        league['playoff_start_week'] = get_league_settings(league["league_key"])
        league_info_file_key = f"{season}/{league_id}/league_info.json"
        s3op.write_json_to_s3(league, league_info_file_key)

    return leagues


def get_league_settings(league_key):
    uri = f"league/{league_key}/settings"
    resp = make_request(uri)
    logger.debug(json.dumps(resp))
    t = objectpath.Tree(resp)

    # for now, we only need playoff_start_week
    jfilter = t.execute('$..league..settings..playoff_start_week')
    for s in jfilter:
        return s
    
    return "-1"

def get_league_stats_categories(league_key):
    pass


def get_league_teams(league_key, league_id):

    # if data already cached in s3, read from s3;
    # otherwise retirive from yahoo and save to s3
    season = utils.get_season()
    file_path = f"{season}/{league_id}/teams.json"
    teams, last_updated = s3op.load_json_from_s3(file_path)

    if teams and last_updated:
        # Check if the data is less than one hour old,
        # because users can change the team name and logo frequently
        now = datetime.now(timezone.utc)
        time_difference = now - last_updated
        if time_difference < timedelta(hours=1):
            logger.debug("Using cached teams data")
            return teams
        
    logger.debug("Try to retrive leagues teams from yahoo.")
    uri = f"league/{league_key}/teams"
    resp = make_request(uri)
    t = objectpath.Tree(resp)
    jfilter = t.execute('$..teams..team..(team_key, team_id, name, team_logos)')
    teams = []

    t = {}
    for p in jfilter:
        # logger.debug(p)
        if ('team_logos' in p):
            t['team_logos'] = p['team_logos'][0]['team_logo']['url']
        else:
            t.update(p)

        # team logo is the last property
        if ('team_logos' in t):
            teams.append(t)
            t = {} 

    # # sort by team id
    teams.sort(key = lambda team : int(team['team_id']))

    logger.debug('teams')
    logger.debug(teams)
    s3op.write_json_to_s3(teams, file_path)
    
    return teams


def get_league_stats(team_keys, game_stat_categories, week=0):
    '''
    Return the stats of a multiple teams for a certain week, or the season(week==0)
    '''
    teams_str = ','.join(team_keys)
    if week==0:
        uri = f"teams;team_keys={teams_str}/stats;type=season"
    else:
        uri = f"teams;team_keys={teams_str}/stats;type=week;week={week}"
    logger.debug(uri)
    resp = make_request(uri)
    logger.debug(json.dumps(resp))
    tree = objectpath.Tree(resp)
    jfilter = tree.execute('$..teams..team..team_stats.stats')

    leagues_stats = []
    data_types = {}
    sort_orders = {}
    for t in jfilter:
        team_stats = {}
        for s in t:
            e = s['stat']
            stat_id = e['stat_id'] 

            # make sure stat_id in game stat categories to filter out display only stat
            if stat_id in game_stat_categories:
                stat_name = game_stat_categories[stat_id]['display_name']
                v = e['value']
                if isinstance(v, str) and '.' in v:
                    v = float(v)
                    data_types[stat_name] ='float'
                else:
                    v = int(v)
                    data_types[stat_name] = 'int'

                team_stats[stat_name] = v

                sort_order = game_stat_categories[stat_id]['sort_order']
                sort_orders[stat_name] = sort_order

        leagues_stats.append(team_stats)

    df = pd.DataFrame(leagues_stats)   
    df = df.astype(data_types)
    
    jfilter = tree.execute('$..teams..team..name')
    team_names = []
    for n in jfilter:
        team_names.append(n)
    df['Team'] = team_names
    df.set_index('Team', inplace=True)

    # jfilter = tree.execute('$..team_points.total')
    # points = []
    # for entry in jfilter:
    #     if entry != '':
    #         point = (float)(entry)
    #         points.append(point)
    
    logger.debug(df)
    logger.debug(sort_orders)
    # logger.debug(points)
    return df, sort_orders




def convert_to_number(value):
    """
    Convert a string to a number, handling special cases like 'INF'.
    
    Parameters:
    - value: The string value to convert.
    
    Returns:
    - The converted number (float or int), or float('inf') for 'INF'.
    """
    if isinstance(value, str):
        if value == 'INF':
            return float('inf') # AT could be infinity if TO is 0
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            # if there is not FGA or FTA, the value is '-'
            return 0  
    elif value is None:
        return 0
    else:
        return value  # if it's already a number
    

def get_league_matchup(league_teams, week, game_stat_categories):
    '''
    Return the matchup for a specified week.
    '''
    team_keys = list(map(lambda x: x['team_key'], league_teams))
    team_names = list(map(lambda x: x['name'], league_teams))
    num_teams = len(league_teams)

    teams_str = ','.join(team_keys)
    uri = f"teams;team_keys={teams_str}/matchups;weeks={week}"
    logger.debug(uri) 

    resp = make_request(uri)
    logger.debug(json.dumps(resp, ensure_ascii=False))
    tree = objectpath.Tree(resp)

    week_info = {}
    jfilter = tree.execute('$..teams..team..matchups..matchup.(week, week_start, week_end, status)') 
    for e in jfilter:
        week_info.update(e)
        break
    # {'week': '4', 'week_start': '2024-11-11', 'week_end': '2024-11-17', 'status': 'postevent'}

    matchups = []
    jfilter = tree.execute('$..teams..team..matchups..matchup..teams..team..name')
    for e in jfilter:
        if e not in matchups:
            matchups.append(e)
    # The 1st and 2nd teams are opposite in the matchup,
    # The 3rd and 4th teams are opposite in the matchup,
    # and so on.
    # ['Zephyr', '蹩脚马_Alpha', "Cupid's Arrow", 'karsitty', '天王', '灰灰', 'JamarrChase', '我还想要一只冰墩墩', 'Mars', 'Prince', 'max', '72wins', 'Melo', 'Sin', '首席NBA', 'SLV', "cao's Ingenious Team", 'lydia']
    week_info['matchups'] = matchups

    # get the matchup score for each team
    jfilter = tree.execute('$..teams..team..matchups..matchup.stat_winners..stat_winner') 
    jfilter_list = list(jfilter)
    num_elements = len(jfilter_list) 
    element_per_team = num_elements / num_teams
    leagues_scores = []
    team_scores = {}    # store the score of each category for a team
    for index, e in enumerate(jfilter_list):
        team_index = int(index / element_per_team)
        stat_id = e['stat_id'] 
        
        # make sure stat_id in game stat categories to filter out display only stat
        if stat_id in game_stat_categories:
            stat_name = game_stat_categories[stat_id]['display_name']
            if 'winner_team_key' in e:
                winner_team_key = e['winner_team_key']
                if winner_team_key == team_keys[team_index]:
                    team_scores[stat_name] = 1  # win
                else:
                    team_scores[stat_name] = 0  # lose
            else:
                team_scores[stat_name] = 0.5    # tie

        # the score of this team is complete
        if (index + 1) % element_per_team == 0:
            leagues_scores.append(team_scores)
            team_scores = {}


    # Assuming leagues_scores and team_names are already defined
    score_df = pd.DataFrame(leagues_scores)
    num_categories = score_df.shape[1]

    # Add new columns
    score_df['Win'] = score_df.apply(lambda row: row.eq(1).sum(), axis=1)
    score_df['Tie'] = score_df.apply(lambda row: row.eq(0.5).sum(), axis=1)
    score_df['Lose'] = num_categories - score_df['Win'] - score_df['Tie']
    score_df['Point'] = score_df['Win'] + score_df['Tie'] / 2
    score_df['Team'] = team_names
    score_df.set_index('Team', inplace=True)
    logger.debug(score_df)

    # Add ranking column
    # score_df = score_df.sort_values(by=['Point', 'Win'], ascending=[False, False])
    # score_df['Rank'] = score_df[['Point', 'Win']].apply(tuple, axis=1).rank(method='min', ascending=False).astype(int)

    # get the raw stats for each team
    jfilter = tree.execute('$..teams..team..matchups..matchup..teams."0".team..team_stats.stats..stat')
    jfilter_list = list(jfilter)
    num_elements = len(jfilter_list) 
    element_per_team = num_elements / num_teams
    leagues_stats = []
    team_stats = {} # store the stats of each category for a team
    for index, e in enumerate(jfilter_list):
        stat_id = e['stat_id'] 

        # make sure stat_id in game stat categories to filter out display only stat
        if stat_id in game_stat_categories:
            stat_name = game_stat_categories[stat_id]['display_name']
            v = convert_to_number(e['value'])
            team_stats[stat_name] = v

        # the stats of this team is complete
        if (index + 1) % element_per_team == 0:
            leagues_stats.append(team_stats)
            team_stats = {}

    stats_df = pd.DataFrame(leagues_stats)   
    team_names = list(map(lambda x: x['name'], league_teams))
    stats_df['Team'] = team_names
    stats_df.set_index('Team', inplace=True)

    return week_info, stats_df, score_df

def get_game_stat_categories():
    '''
    Return all available stat categories of the game(NBA),
    used to dynamically create the stat table.
    '''
    logger.debug("get_game_stat_categories")
    
    # if data already cached in s3 recently, read from s3;
    # otherwise retirive from yahoo and save to s3
    file_path = 'game_stat_categories.json'
    categories, last_updated = s3op.load_json_from_s3(file_path)

    if categories and last_updated:
        # Check if the data is less than one year old
        # because the game stat categories rarely change
        now = datetime.now(timezone.utc)
        time_difference = now - last_updated
        if time_difference < timedelta(days=365):
            logger.debug("Using cached game stat category data")
            logger.debug(json.dumps(categories, indent=4))
            return categories
        
    logger.debug("Try to retrive game stat categories from yahoo.")
    categories = {}
    uri = 'game/nba/stat_categories'
    resp = make_request(uri)
    t = objectpath.Tree(resp)
    jfilter = t.execute('$..stat_categories..stats..(stat_id, display_name, sort_order)')

    for c in jfilter:
        if 'stat_id' in c and 'display_name' in c and 'sort_order' in c:
            categories[c['stat_id']] = c

    logger.debug('categories')
    logger.debug(categories)
    s3op.write_json_to_s3(categories, file_path)
    
    return categories

def make_request(path): 
    """Send an API request to the URI and return the response as JSON

    :param uri: URI of the API to call
    :type uri: str
    :return: JSON document of the response
    :raises: RuntimeError if any response comes back with an error
    """
    url = f'{cfg.FANTASY_API_URL}/{path}'
    logger.debug(f'request url: {url}')

    headers = {
        'Authorization': 'Bearer ' + ACCESS_TOKEN
    }

    response = requests.get(url, params={'format': 'json'}, headers = headers)

    if response.status_code != 200:
        logger.error('request to {} failed with error code {}'.format(url, response.status_code))
        raise RuntimeError(response.content)

    jresp = response.json()
    return jresp