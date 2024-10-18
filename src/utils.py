import boto3
import json
import os
import datetime
from scipy.stats import rankdata
from io import StringIO
import pandas as pd
import config
from config import logger

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


def load_json_from_s3(file_key, bucket_name = None):

    if bucket_name is None:
        bucket_name = config.S3_Bucket
        
    logger.debug(f"Try to get file {file_key} from s3 bucket {bucket_name}.")
    s3 = boto3.resource('s3')
     
    try:
        obj = s3.Object(bucket_name, file_key)
        body = obj.get()['Body'].read().decode('utf-8')
        json_content = json.loads(body)
        logger.debug(f"Successfully't get object {file_key} from bucket {bucket_name}.")
        logger.debug(json_content)
        return json_content

    except Exception as e:
        logger.debug(f"Couldn't get object {file_key} from bucket {bucket_name}.")
        logger.debug(e)
        return None

def write_json_to_s3(json_data, file_key, bucket_name = None):

    if bucket_name is None:
        bucket_name = config.S3_Bucket
        
    logger.debug(f"Try to save file {file_key} to s3 bucket {bucket_name}.")
    
    s3 = boto3.resource('s3')  
    
    try:
        json_content = json.dumps(json_data, ensure_ascii=False, indent=4)
        s3.Object(bucket_name, file_key).put(Body=json_content, ContentType='application/json')
        logger.debug(f"Successfully saved JSON to {bucket_name}/{file_key}")
    except Exception as e:
        logger.debug(f"An error occurred: {e}")


def load_dataframe_from_csv_on_s3(file_key, bucket_name = None):
    if bucket_name is None:
        bucket_name = config.S3_Bucket

    logger.debug(f"Try to load csv file {file_key} from s3 bucket {bucket_name}.")

    s3 = boto3.resource('s3')   
    try:
        obj = s3.Object(bucket_name, file_key)
        csv_string = obj.get()['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_string))
        return df

    except Exception as e:
        logger.debug(f"Couldn't get object {file_key} from bucket {bucket_name}.")
        logger.debug(e)
        return None    

def write_dataframe_to_csv_on_s3(df, file_key, bucket_name = None):
    if bucket_name is None:
        bucket_name = config.S3_Bucket

    file_path = f"s3://{bucket_name}/{file_key}"
   
    try:
        df.to_csv(file_path, encoding='utf_8_sig', index=True, index_label='Team')
        logger.debug(f"Successfully saved dataframe to {file_path}")
    except Exception as e:
        logger.debug(f"An error occurred when writing dataframe to {file_path}: {e}")
    
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


def stat_to_score(stat_df, sort_orders):
    '''Give then stats of a league for a week or the whole season, compute the ranking score
    '''
    score_df = stat_df.copy()

    idx = 0
    for (stat_name, stat_value) in stat_df.items():
        sort_order = sort_orders[idx]
        idx += 1

        reverse = (sort_order == '0')
        scores = data_to_ranking_score(stat_value.values, reverse)
        score_df[stat_name] = scores

    # add a column to display the total score of each team (row)
    score_df['Total'] = score_df.sum(axis=1)

    return score_df

def data_to_ranking_score(values, reverse = False):
    '''
    Given a list of value, return a list of ranking score.
    If reverse = False, the biggest value will get the biggest ranking score.
    If reverse = True, the biggest value will get the smallest ranking score.
    Only category 'TO' should set 'reverse' to 'True'.

    The smallest ranking score is 1, the biggest ranking score is the element
    number of this list.
    '''
    scores = rankdata(values)
    if reverse:
        scores = [(len(values) + 1 - score) for score in scores]

    return scores