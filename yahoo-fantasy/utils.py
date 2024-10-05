import boto3
import os
import time
from datetime import datetime

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

def isValidSession(sessionId):
    
    if sessionId is None or sessionId == '':
        return False

    logger.info('try to find session in db')        
    dynamodb = boto3.resource('dynamodb') 
    table = dynamodb.Table(os.environ.get("DynamoDB_Table")) 

    resp  = table.get_item(Key={"sessionId": sessionId})
    if 'Item' in resp:
        expiration_time = float(resp['Item']['expiration_time'])
        now = time.time()
        # expiring soon (in 1 minute), refresh token
        if expiration_time - now < 60:  
            logger.info("expiring in 1 minute, need to refresh token.  Expiration time: {}, Now:{}".format(datetime.fromtimestamp(expiration_time), datetime.fromtimestamp(now)))
            return True
        else:
            logger.info("Session already expires.  Expiration time: {}, Now:{}".format(datetime.fromtimestamp(expiration_time), datetime.fromtimestamp(now)))
            return False
    else:
        logger.info("SessionId {} not found in db".format(sessionId))
        return False