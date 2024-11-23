#!/usr/bin/env python

from io import StringIO, BytesIO
import boto3
import json
import os
import pandas as pd
import config as cfg

logger = cfg.logger

def load_json_from_s3(file_key):

    bucket_name = os.environ.get("DATA_BUCKET_NAME")

    file_key = 'data/' + file_key
        
    logger.debug(f"Try to get file {file_key} from s3 bucket {bucket_name}.")
    s3 = boto3.client('s3')
    
    try:
        # Get the object metadata
        head_response = s3.head_object(Bucket=bucket_name, Key=file_key)
        last_modified = head_response['LastModified']
        
        # Get the object content
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        content = response['Body'].read().decode('utf-8')
        json_data = json.loads(content)
        
        return json_data, last_modified
    
    except s3.exceptions.NoSuchKey:
        print(f"The file {file_key} does not exist in the bucket {bucket_name}.")
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def write_json_to_s3(json_data, file_key):

    bucket_name = os.environ.get("DATA_BUCKET_NAME")

    file_key = 'data/' + file_key
        
    logger.debug(f"Try to save file {file_key} to s3 bucket {bucket_name}.")
    
    s3 = boto3.resource('s3')  
    
    try:
        json_content = json.dumps(json_data, ensure_ascii=False, indent=4)
        s3.Object(bucket_name, file_key).put(Body=json_content, ContentType='application/json')
        logger.debug(f"Successfully saved JSON to {bucket_name}/{file_key}")
    except Exception as e:
        logger.debug(f"An error occurred: {e}")


def load_dataframe_from_csv_on_s3(file_key):

    bucket_name = os.environ.get("DATA_BUCKET_NAME")

    file_key = 'data/' + file_key

    logger.debug(f"Try to load csv file {file_key} from s3 bucket {bucket_name}.")

    s3 = boto3.resource('s3')   
    try:
        obj = s3.Object(bucket_name, file_key)
        csv_string = obj.get()['Body'].read().decode('utf-8')
        # Read the CSV file and set the first column as the index
        df = pd.read_csv(StringIO(csv_string), index_col=0)
        return df

    except Exception as e:
        logger.debug(f"Couldn't get object {file_key} from bucket {bucket_name}.")
        logger.debug(e)
        return None    

def write_dataframe_to_csv_on_s3(df, file_key):

    bucket_name = os.environ.get("DATA_BUCKET_NAME")
    file_key = 'data/' + file_key

    file_path = f"s3://{bucket_name}/{file_key}"
   
    try:
        df.to_csv(file_path, encoding='utf_8_sig', index=True, index_label='Team')
        logger.debug(f"Successfully saved dataframe to {file_path}")
    except Exception as e:
        logger.debug(f"An error occurred when writing dataframe to {file_path}: {e}")


def write_styled_dataframe_to_excel_on_s3(styled_dfs, sheet_names, file_key):

    # Save the styled DataFrame to an Excel file in memory
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:

        for styled_df, sheet_name in zip(styled_dfs, sheet_names):
            styled_df.to_excel(writer, sheet_name=sheet_name)

    # Reset the buffer position to the beginning after writing
    excel_buffer.seek(0)

    # Upload the file to S3
    s3 = boto3.client('s3')
    bucket_name = os.environ.get("DATA_BUCKET_NAME")
    file_key = 'data/' + file_key

    try:
        s3.upload_fileobj(excel_buffer, bucket_name, file_key)
        print(f"File uploaded to S3 at s3://{bucket_name}/{file_key}")
    except Exception as e:
        print(f"Failed to upload file to S3: {e}")


def write_image_to_s3(img_data, file_key):

    bucket_name = os.environ.get("DATA_BUCKET_NAME")
    
    file_key = 'data/' + file_key
        
    logger.debug(f"Try to save file {file_key} to s3 bucket {bucket_name}.")
    
    s3 = boto3.resource('s3')  
    
    try:
        s3.Object(bucket_name, file_key).put(Body=img_data, ContentType='image/png')
        logger.debug(f"Successfully saved image to {bucket_name}/{file_key}")
    except Exception as e:
        logger.debug(f"An error occurred: {e}")


def write_styled_dataframe_to_html_on_s3(styled_df, file_key, roto = True):
    bucket_name = os.environ.get("DATA_BUCKET_NAME")
    file_key = 'data/' + file_key

    # Convert styled DataFrame to HTML with inline CSS for font and column width
    if roto:
        html_data = styled_df.set_table_attributes('class="table table-striped table-sm"').to_html()
    else:
        html_data = styled_df.set_table_attributes('class="table table-sm"').to_html()

    s3 = boto3.resource('s3')
    try:
        s3.Object(bucket_name, file_key).put(Body=html_data, ContentType='text/html')
        logger.debug(f"Successfully saved HTML to {bucket_name}/{file_key}")
    except Exception as e:
        logger.debug(f"An error occurred: {e}")

    logger.debug(f"File uploaded to S3 at s3://{bucket_name}/{file_key}")


def load_html_from_s3_as_str(file_key):
    bucket_name = os.environ.get("DATA_BUCKET_NAME")

    file_key = 'data/' + file_key
        
    logger.debug(f"Try to get file {file_key} from s3 bucket {bucket_name}.")
    s3 = boto3.client('s3')
    
    try:
        # Get the object content
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        content = response['Body'].read().decode('utf-8')
        
        return content
    
    except s3.exceptions.NoSuchKey:
        logger.error(f"The file {file_key} does not exist in the bucket {bucket_name}.")
        return None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


def remove_all_files_in_folder_in_s3(folder_key):
    """
    Remove all files under a folder in an S3 bucket.
    
    Parameters:
    - folder_key: The name of the folder (prefix) in the S3 bucket.
    """

    bucket_name = os.environ.get("DATA_BUCKET_NAME")

    folder_key = 'data/' + folder_key

    s3 = boto3.client('s3')

    # List all objects in the specified folder
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_key)

    if 'Contents' in response:
        # Extract the keys of the objects to delete
        objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]

        # Delete the objects
        s3.delete_objects(Bucket=bucket_name, Delete={'Objects': objects_to_delete})

        logger.debug(f"Deleted {len(objects_to_delete)} objects from {folder_key} in bucket {bucket_name}.")
    else:
        logger.debug(f"No objects found in {folder_key} in bucket {bucket_name}.")