from datetime import datetime, timedelta, timezone


def getNow ():
    tz = timezone(timedelta(hours=8))
    return str(datetime.now(tz)).split('.')[0];

def convertSeconds (n):
    d = h = m = s = 0
    s = n % 60
    n = round(n // 60)
    m = n % 60
    if not n: return f'{s:.3f} s'
    n //= 60
    h = n % 24
    if not n: return f'{m} min {s:.3f} s'
    d = n // 24
    if not d: return f'{h} h {m} min {s:.3f} s'
    return f'{d} d {h} h {m} min {s:.3f} s'

def getToday():
    "获得今天的日期，格式为'%Y%m%d'"
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime('%Y%m%d')