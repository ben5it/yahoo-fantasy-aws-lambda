#!/usr/bin/env python

from io import StringIO, BytesIO
import boto3
# import imgkit
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
        df = pd.read_csv(StringIO(csv_string))
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

# Configure imgkit to use wkhtmltopdf
# config = imgkit.config(wkhtmltoimage='/usr/local/bin/wkhtmltoimage')  # Adjust path if needed


# def write_styled_dataframe_to_image_on_s3(styled_df, file_key):

#     bucket_name = os.environ.get("DATA_BUCKET_NAME")
    
#     file_key = 'data/' + file_key

#     # Convert styled DataFrame to HTML with inline CSS for font and column width
#     html = styled_df.set_table_attributes('class="table table-striped table-sm"').to_html(index=True)

#     # Add CSS to center the caption
#     html = f"""
#     <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">  
#     <div class="container" style="width: 600px;"> 
#     {html}
#     </div>
#     """
    
#     # Convert the styled DataFrame to an image
#     temp_file_path = '/tmp/styled_dataframe.png'

#     # Convert HTML to image using imgkit
#     imgkit.from_string(html, temp_file_path, config=config)

#     # Read the temporary file into a BytesIO object
#     with open(temp_file_path, 'rb') as f:
#         buf = BytesIO(f.read())

#     s3 = boto3.client('s3')
#     # Upload image to S3
#     s3.put_object(Bucket=bucket_name, Key=file_key, Body=buf.getvalue(), ContentType='image/png')

#     logger.debug(f"File uploaded to S3 at s3://{bucket_name}/{file_key}")


def write_styled_dataframe_to_html_on_s3(styled_df, file_key):
    bucket_name = os.environ.get("DATA_BUCKET_NAME")
    file_key = 'data/' + file_key

    # Convert styled DataFrame to HTML with inline CSS for font and column width
    html_data = styled_df.set_table_attributes('class="table table-striped table-sm"').to_html()

    html_data = f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <link rel="icon" type="image/svg+xml" href="/vite.svg" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>鸭虎饭特稀</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">   
    </head>
    <body>
        <div class="container">
        {html_data}
        </div>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

    s3 = boto3.resource('s3')
    try:
        s3.Object(bucket_name, file_key).put(Body=html_data, ContentType='text/html')
        logger.debug(f"Successfully saved HTML to {bucket_name}/{file_key}")
    except Exception as e:
        logger.debug(f"An error occurred: {e}")

    logger.debug(f"File uploaded to S3 at s3://{bucket_name}/{file_key}")