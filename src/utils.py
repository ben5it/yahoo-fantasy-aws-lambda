import boto3
import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import os
import datetime

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


def get_json_from_s3(file_key, bucket_name = None):

    if bucket_name is None:
        bucket_name = config.S3_Bucket
        
    logger.info(f"Try to get file {file_key} from s3 bucket {bucket_name}.")
    s3 = boto3.resource('s3')
     
    try:
        obj = s3.Object(bucket_name, file_key)
        body = obj.get()['Body'].read().decode('utf-8')
        json_content = json.loads(body)
        logger.info(f"Successfully't get object {file_key} from bucket {bucket_name}.")
        logger.info(json_content)
        return json_content

    except ClientError as e:
        logger.info(f"Couldn't get object {file_key} from bucket {bucket_name}.")
        logger.info(e)
        return None

def save_json_to_s3(json_data, file_key, bucket_name = None):

    if bucket_name is None:
        bucket_name = config.S3_Bucket
        
    logger.info(f"Try to save file {file_key} to s3 bucket {bucket_name}.")
    
    s3 = boto3.client('s3')
    
    try:
        json_content = json.dumps(json_data, ensure_ascii=False, indent=4)
        s3.put_object(Bucket=bucket_name, Key=file_key, Body=json_content, ContentType='application/json')
        logger.info(f"Successfully saved JSON to {bucket_name}/{file_key}")
    except (NoCredentialsError, PartialCredentialsError):
        logger.info("AWS credentials not found or incomplete.")
    except ClientError as e:
        logger.info(f"An error occurred: {e}")

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
#     logger.info('get object from s3 bucket {}/{}', config.S3_Bucket, path)
#     logger.info(resp)


    