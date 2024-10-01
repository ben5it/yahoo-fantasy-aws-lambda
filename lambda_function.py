import json
import os
import requests
import urllib.parse
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    
    Client_ID = os.environ.get('Client_ID')
    Client_Secrect = os.environ.get('Client_Secrect')

    AUTHORIZE_URL="https://api.login.yahoo.com/oauth2/request_auth"
    ACCESS_TOKEN_URL="https://api.login.yahoo.com/oauth2/get_token"
    CALLBACK_URL = "https://d3aibao6jz53if.cloudfront.net/api/callback"
    
    # print(event)
    # print(context)

    path = event['rawPath']
    print('path',path)
    if path =='/api/login':
        data = { 'response_type' : 'code', 'redirect_uri' : CALLBACK_URL, 'scope': 'openid', 'client_id' : Client_ID}
        login_url  = AUTHORIZE_URL + '?' + urllib.parse.urlencode(data)
        logger.info('Login URL： %s', login_url)
        return {
            "isBase64Encoded": False,
            "statusCode": 302,
            "headers": {
                  "Location": login_url
            },
            "multiValueHeaders": {},
            "body": ""
        }
    elif path == '/api/callback':
        print('login callback')
        # print(event)
        parms = urllib.parse.parse_qs(event['rawQueryString'])
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
            return {
                'statusCode': 200,
                'body': code
           }
    