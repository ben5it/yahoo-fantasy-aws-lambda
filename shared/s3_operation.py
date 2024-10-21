#!/usr/bin/env python

from io import StringIO
import boto3
import json
import os
import pandas as pd

from config import logger

def load_json_from_s3(file_key):

    bucket_name = os.environ.get("S3_BUCKET_NAME")
        
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

def write_json_to_s3(json_data, file_key):

    bucket_name = os.environ.get("S3_BUCKET_NAME")
        
    logger.debug(f"Try to save file {file_key} to s3 bucket {bucket_name}.")
    
    s3 = boto3.resource('s3')  
    
    try:
        json_content = json.dumps(json_data, ensure_ascii=False, indent=4)
        s3.Object(bucket_name, file_key).put(Body=json_content, ContentType='application/json')
        logger.debug(f"Successfully saved JSON to {bucket_name}/{file_key}")
    except Exception as e:
        logger.debug(f"An error occurred: {e}")


def load_dataframe_from_csv_on_s3(file_key):

    bucket_name = os.environ.get("S3_BUCKET_NAME")

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

def write_dataframe_to_csv_on_s3(df, file_key):

    bucket_name = os.environ.get("S3_BUCKET_NAME")

    file_path = f"s3://{bucket_name}/{file_key}"
   
    try:
        df.to_csv(file_path, encoding='utf_8_sig', index=True, index_label='Team')
        logger.debug(f"Successfully saved dataframe to {file_path}")
    except Exception as e:
        logger.debug(f"An error occurred when writing dataframe to {file_path}: {e}")


def write_image_to_s3(img_data, file_key):

    bucket_name = os.environ.get("S3_BUCKET_NAME")
        
    logger.debug(f"Try to save file {file_key} to s3 bucket {bucket_name}.")
    
    s3 = boto3.resource('s3')  
    
    try:
        s3.Object(bucket_name, file_key).put(Body=img_data, ContentType='image/png')
        logger.debug(f"Successfully saved image to {bucket_name}/{file_key}")
    except Exception as e:
        logger.debug(f"An error occurred: {e}")