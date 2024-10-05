import boto3
import os
import time


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

