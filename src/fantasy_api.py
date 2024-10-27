#!/usr/bin/env python

import json
import objectpath
import pandas as pd
import requests


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
    t = objectpath.Tree(resp)
    jfilter = t.execute('$..leagues..(league_key, league_id, name, logo_url, scoring_type, start_date, end_date, current_week, start_week, end_week)')

    leagues = []
    for l in jfilter:
        leagues.append(l)

    # sort by league id
    leagues.sort(key = lambda league : int(league['league_id']))

    logger.info('leagues')
    logger.info(leagues)
    # [{"league_key": "428.l.7124", "league_id": "7124", "name": "Never Ending", "logo_url": false, "scoring_type": "head", "start_date": "2023-10-24", "end_date": "2024-04-14", "current_week": 24, "start_week": "1", "end_week": "24"}, {"league_key": "428.l.23476", "league_id": "23476", "name": "2023~2024 Gamma", "logo_url": "https://yahoofantasysports-res.cloudinary.com/image/upload/t_s192sq/fantasy-logos/88a86479d6cf4bc472623e59484ab6c70e397336290032a9c744125e158d2c21.jpg", "scoring_type": "head", "start_date": "2023-10-24", "end_date": "2024-04-14", "current_week": 24, "start_week": "1", "end_week": "24"}]

    for league in leagues:
        league_id = league["league_id"]
        league_info_file_key = f"{season}/{league_id}/league_info.json"
        s3op.write_json_to_s3(league, league_info_file_key)

    return leagues


def get_league_info(league_key, league_id):
    pass

def get_league_stats_categories(league_key):
    pass


def get_league_teams(league_key, league_id):

    # if data already cached in s3, read from s3;
    # otherwise retirive from yahoo and save to s3
    season = utils.get_season()
    file_path = f"{season}/{league_id}/teams.json"
    teams = s3op.load_json_from_s3(file_path)
    if teams is not None:
        logger.debug(json.dumps(teams, indent=4))  
    else:
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

    jfilter = tree.execute('$..team_points.total')
    points = []
    for entry in jfilter:
        if entry != '':
            point = (float)(entry)
            points.append(point)
    
    logger.debug(df)
    logger.debug(sort_orders)
    logger.debug(points)
    return df, sort_orders, points




def get_league_schedule(league_id):
    pass

def get_league_matchup(team_keys, week):
    '''
    Return the matchup for a specified week.
    '''
    teams_str = ','.join(team_keys)
    uri = f"teams;team_keys={teams_str}/matchups;weeks={week}"
    logger.debug(uri) 

    # week_matchup = {}
    resp = make_request(uri)
    logger.debug(resp)
    tree = objectpath.Tree(resp)
    # jfilter = tree.execute('$..teams..team..matchups..matchup.(week, week_start, week_end)')
    # for e in jfilter:
    #     logger.debug(e)
    #     # {'week': '2', 'week_start': '2023-10-30', 'week_end': '2023-11-05'}
    #     week_matchup = e
    #     break

    teams = []
    jfilter = tree.execute('$..teams..team..matchups..matchup..teams..team..name')
    for e in jfilter:
        # logger.debug(e)
        if e not in teams:
            teams.append(e)
    logger.debug('Week {} Match up'.format(week))
    for i in range(0, len(teams), 2 ): 
        logger.debug('{} VS {}'.format(teams[i], teams[i+1])) 

    # week_matchup['matchup'] = teams
    # logger.info(week_matchup) 

    return teams

def get_game_stat_categories():
    '''
    Return all available stat categories of the game(NBA),
    used to dynamically create the stat table.
    '''
    logger.debug("get_game_stat_categories")
    
    # if data already cached in s3, read from s3;
    # otherwise retirive from yahoo and save to s3
    file_path = 'game_stat_categories.json'
    categories = s3op.load_json_from_s3(file_path)
    if categories is not None:
        logger.debug(json.dumps(categories, indent=4))  
    else:
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