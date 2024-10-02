import json
import os
import requests
from urllib.parse import urlencode, quote, parse_qs
import logging
import base64
import jwt
import time
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    
    Client_ID = os.environ.get('Client_ID')
    Client_Secrect = os.environ.get('Client_Secret')
    print(Client_Secrect)

    AUTHORIZE_URL="https://api.login.yahoo.com/oauth2/request_auth"
    ACCESS_TOKEN_URL="https://api.login.yahoo.com/oauth2/get_token"
    CALLBACK_URL = "https://d3aibao6jz53if.cloudfront.net/callback"
    
    # print(event)
    # print(context)

    path = event['rawPath']
    print('path',path)
    if path =='/login':
        data = { 
            'client_id' : Client_ID,
            'response_type' : 'code', 
            'redirect_uri' : CALLBACK_URL, 
            'scope': "openid"
        }
        login_url  = AUTHORIZE_URL + '?' + urlencode(data, quote_via=quote)
        logger.info('Login URL： %s', login_url)
        sessionId = str(uuid.uuid4())
        theme = 'blue moon'
        return {
            "isBase64Encoded": False,
            "statusCode": 302,
            "headers": {
                "Location": login_url
            },
            "multiValueHeaders": {
                "Set-Cookie": ["cookie1=chocolate-chip", "cookie2=oatmeal"]
            },
            "body": ""
        }
    elif path == '/callback':
        print('login callback')
        print(event)
        parms = parse_qs(event['rawQueryString'])
        # print(parms)
        if 'code' not in parms:
            logger.error("Code Missing.")
            return {
                'statusCode': 401,
                'body': 'Code Missing' 
            }
        else:
            code = parms['code'][0]
            
            encoded_credentials = base64.b64encode(('{0}:{1}'.format(Client_ID, Client_Secrect)).encode('utf-8'))

            headers = {
                'Authorization': 'Basic {0}'.format(encoded_credentials.decode('utf-8')),
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data =  {
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": CALLBACK_URL
            }
        
            raw_token = requests.post(ACCESS_TOKEN_URL, data=data, headers = headers)
            parsed_token = raw_token.json()
            logger.info(parsed_token)
            access_token = parsed_token["access_token"]
            refresh_token = parsed_token["refresh_token"]
            expiration_time = time.time() + parsed_token["expires_in"]
            id_token = jwt.decode(parsed_token["id_token"], options={"verify_signature": False})
            user_id = id_token['sub']
            profile_image = id_token['profile_images']['image32']
            nickname = id_token['nickname']
            email = id_token['email']
            logger.info("access_token %s", access_token)
            logger.info("refresh_token %s", refresh_token)
            logger.info("id_token %s", id_token)
            logger.info("user_id %s", user_id)
            # return {
            #     "isBase64Encoded": False,
            #     "statusCode": 302,
            #     "headers": {
            #         "Location": "https://d3aibao6jz53if.cloudfront.net"
            #     },
            #     "multiValueHeaders": {"Set-Cookie": ["cookie3=chocolate-chip2", "cookie4=oatmeal"]},
            #     "body": json.dumps({
            #         "sessionId": str(uuid.uuid4()),
            #         "userId": user_id
            #     })
            # }
            return {
                'statusCode': 401,
                'body': json.dumps(id_token)
            }