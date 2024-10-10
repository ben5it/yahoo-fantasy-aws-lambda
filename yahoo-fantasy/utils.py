import boto3
import os
import datetime


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

