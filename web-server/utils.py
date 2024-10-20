#!/usr/bin/env python

# import json
# import os
import datetime
# import s3_operation as s3op
# import pytz
# import config
# from config import logger

def getSessionIdFromCookies(cookies):
    
    sessionId = None
    
    for cookie in cookies:
        pair = cookie.split('=')
        key = pair[0]
        if key == 'sessionId':
            sessionId = pair[1]
            break

    return sessionId


def getDefaultSeason():
    today = datetime.date.today()
    season = today.year
    if today.month < 10 or (today.month == 10 and today.day < 20): # nba season usually starts at the end of Oct
        season -= 1   
    
    return season


# def getPredictWeek(league_id):
#     season = getDefaultSeason()
#     league_info_file_key = f"data/{season}/{league_id}/league_info.json"
#     league_info = s3op.load_json_from_s3(league_info_file_key)

#     current_week = int(league_info['current_week'])
#     end_week = int(league_info['end_week'])
#     today = datetime.datetime.now(pytz.timezone('US/Pacific')).date()
#     weekday = today.weekday()

#     predict_week = current_week + 1
#     # if it is Monday, set predict week to current week
#     # because this is used for research the matchup
#     if weekday < 1:
#         predict_week -= 1
#     if predict_week > end_week:
#         predict_week = end_week

#     return 2
#     return predict_week


# def isDataUpToDate(league_id, week):
#     s3 = boto3.client('s3')
#     season = getDefaultSeason
#     path = f'data/{season}/{league_id}/{week:02d}/stats.csv'
#     resp = s3.get_object(
#         Bucket=config.S3_Bucket,
#         # IfMatch='string',
#         # IfModifiedSince=datetime(2015, 1, 1),
#         # IfNoneMatch='string',
#         # IfUnmodifiedSince=datetime(2015, 1, 1),
#         # Range='string',
#         # ResponseCacheControl='string',
#         # ResponseContentDisposition='string',
#         # ResponseContentEncoding='string',
#         # ResponseContentLanguage='string',
#         # ResponseContentType='string',
#         # ResponseExpires=datetime(2015, 1, 1),
#         # VersionId='string',
#         # SSECustomerAlgorithm='string',
#         # SSECustomerKey='string',
#         # RequestPayer='requester',
#         # PartNumber=123,
#         # ExpectedBucketOwner='string',
#         # ChecksumMode='ENABLED',
#         Key=path
#     )
#     logger.debug('get object from s3 bucket {}/{}', config.S3_Bucket, path)
#     logger.debug(resp)


