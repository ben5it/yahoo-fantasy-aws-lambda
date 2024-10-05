import json
import os
import requests
from urllib.parse import urlencode, quote, parse_qs

import base64
import jwt
import time
import uuid
import boto3
from decimal import Decimal
import config

from config import logger

def login():
    data = { 
        'client_id' : config.Client_ID,
        'response_type' : 'code', 
        'redirect_uri' : config.LOGIN_CALLBACK_URL, 
        'scope': "openid"
    }
    login_url  = config.AUTHORIZE_URL + '?' + urlencode(data, quote_via=quote)
    logger.info('Login URL： %s', login_url)
    return {
        "isBase64Encoded": False,
        "statusCode": 302,
        "headers": {
            "Location": login_url
        }
    }


def callback(queryString):

    logger.info('Raw Query String： %s', queryString)
    parms = parse_qs(queryString)

    if 'code' not in parms:
        logger.error("Code Missing in query string.")
        return {
            'statusCode': 401,
            'body': 'Code missing in query string' 
        }

    else:
        code = parms['code'][0]
        
        encoded_credentials = base64.b64encode(('{0}:{1}'.format(config.Client_ID, config.Client_Secrect)).encode('utf-8'))

        headers = {
            'Authorization': 'Basic {0}'.format(encoded_credentials.decode('utf-8')),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data =  {
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": config.LOGIN_CALLBACK_URL
        }
    
        raw_token = requests.post(config.ACCESS_TOKEN_URL, data=data, headers = headers)
        parsed_token = raw_token.json()
        logger.debug(parsed_token)
        if 'error' in parsed_token:
            return {
                'statusCode': 401,
                'body': parsed_token['error_description']
            }
        else:
            access_token = parsed_token["access_token"]
            refresh_token = parsed_token["refresh_token"]
            expiration_time = time.time() + parsed_token["expires_in"]
            id_token = jwt.decode(parsed_token["id_token"], options={"verify_signature": False})
            user_id = id_token['sub']
            profile_image = id_token['profile_images']['image32']
            nickname = id_token['nickname']
            email = id_token['email']
            sessionId =str(uuid.uuid4())
            data = {
                'sessionId': sessionId, 
                'userId': user_id,
                'nickname': nickname,
                'email': email,                   
                'profile_image':profile_image,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expiration_time':expiration_time                
            }
            logger.info(data)
            ddb_data = json.loads(json.dumps(data), parse_float=Decimal)
            dynamodb = boto3.resource('dynamodb') 
            logger.info('DynamoDB_Table： %s', config.DynamoDB_Table)
            table = dynamodb.Table(config.DynamoDB_Table) 
            #inserting values into table 
            response = table.put_item(Item = ddb_data) 
            
            return {
                "cookies" : [f"sessionId={sessionId}"],
                "isBase64Encoded": False,
                "statusCode": 302,
                "headers": {
                    "Location": config.BASE_URL
                },
                "body": ""
            }




