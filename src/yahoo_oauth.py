import json
import os
import requests
from urllib.parse import urlencode, quote, parse_qs

import base64
import jwt
import time
from datetime import datetime, timedelta
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
    logger.debug('Login URL： %s', login_url)
    return {
        "isBase64Encoded": False,
        "statusCode": 302,
        "headers": {
            "Location": login_url
        }
    }


def callback(queryString):

    logger.debug('Raw Query String： %s', queryString)
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
            expiration_time = int(time.time() + parsed_token["expires_in"])
            id_token = jwt.decode(parsed_token["id_token"], options={"verify_signature": False})
            user_id = id_token['sub']
            profile_image = id_token['profile_images']['image32']
            nickname = id_token['nickname']
            email = id_token['email']
            sessionId =str(uuid.uuid4())

            # Calculate the expiration time of this item (1 days from now) in epoch second format
            ttl = int((datetime.now() + timedelta(days=1)).timestamp())
            data = {
                'sessionId': sessionId, 
                'userId': user_id,
                'nickname': nickname,
                'email': email,                   
                'profile_image':profile_image,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expiration_time':expiration_time,
                'expireAt': ttl             
            }
            logger.debug(data)
            ddb_data = json.loads(json.dumps(data), parse_float=Decimal)
            dynamodb = boto3.resource('dynamodb') 
            logger.debug('DynamoDB_Table： %s', config.DynamoDB_Table)
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

def isValidSession(sessionId):
    
    if sessionId is None or sessionId == '':
        return False, None

    logger.debug('try to find session in db')        
    dynamodb = boto3.resource('dynamodb') 
    table = dynamodb.Table(config.DynamoDB_Table) 

    resp  = table.get_item(Key={"sessionId": sessionId})
    if 'Item' in resp:
        expiration_time = float(resp['Item']['expiration_time'])
        userId = resp['Item']['userId']
        access_token = resp['Item']['access_token']

        now = time.time()

        if expiration_time - now < 0: 
            logger.debug("Session already expires.  Expiration time: {}, Now:{}".format(datetime.fromtimestamp(expiration_time), datetime.fromtimestamp(now)))
            return False, access_token  
        # expiring soon (in 5 minute), refresh token
        elif expiration_time - now < 300:  
            logger.debug("expiring in 5 minute, need to refresh token.  Expiration time: {}, Now:{}".format(datetime.fromtimestamp(expiration_time), datetime.fromtimestamp(now)))
            current_refresh_token = resp['Item']['refresh_token']
            refresh_token(sessionId, current_refresh_token)
            return True, access_token
        else:
            logger.debug("Find valid session id db")
            return True, access_token
    else:
        logger.debug("SessionId {} not found in db".format(sessionId))
        return False

def refresh_token(sessionId, current_refresh_token):
    encoded_credentials = base64.b64encode(('{0}:{1}'.format(config.Client_ID, config.Client_Secrect)).encode('utf-8'))

    headers = {
        'Authorization': 'Basic {0}'.format(encoded_credentials.decode('utf-8')),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data =  {
        "refresh_token": current_refresh_token,
        "grant_type": "refresh_token",
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

        # update the time to live of this item
        ttl = int((datetime.now() + timedelta(days=1)).timestamp())
        dynamodb = boto3.resource('dynamodb') 
        logger.debug('update access token to dynamodb table %s', config.DynamoDB_Table)
        table = dynamodb.Table(config.DynamoDB_Table) 
        #inserting values into table 
        response = table.update_item(
            Key={'sessionId': sessionId},
            UpdateExpression='SET access_token=:val1, refresh_token=:val2, expiration_time=:val3, expireAt=:val4',
            ExpressionAttributeValues =json.loads(json.dumps({
                ':val1':  access_token,
                ':val2':  refresh_token,
                ':val3':  expiration_time,
                ':val4': ttl
            }), parse_float=Decimal),
            ReturnValues="UPDATED_NEW"
        )
        logger.debug(response["Attributes"])


