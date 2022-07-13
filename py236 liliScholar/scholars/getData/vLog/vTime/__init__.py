from datetime import datetime, timedelta, timezone


def getNow ():
    tz = timezone(timedelta(hours=8))
    return str(datetime.now(tz)).split('.')[0];

def getToday():
    "获得今天的日期，格式为'%Y%m%d'"
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime('%Y%m%d')