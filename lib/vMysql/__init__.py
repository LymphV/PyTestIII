import pandas as pd
from .utils import isNull, stdSqlData, stdSqlCol

__version__ = 20210608
__author__ = 'LymphV@163.com'

dbs = []
def addDb (db):
    dbs.append(db)


def sql(s):
    cursor = dbs[-1].cursor()
    cursor.execute(s)
    rst = cursor.fetchall()
    
    rst = pd.DataFrame(rst, columns=[*zip(*cursor.description)][0] if cursor.description else [])
    cursor.close()
    return rst

def describe (table):
    rst = sql(f'describe {table};')
    rst.columns.name = table
    return rst

def select (items, table, *args, **kwargs):
    if type(items) is str:
        items = items.split(',')
    item = ','.join([stdSqlCol(x) for x in items])
        
    if args:
        r = range(*args)
        start, stop = r.start, r.stop
        limit = f'limit {start}, {stop - start}'
    else: limit = ''
    
    s = f'select {item} from {stdSqlCol(table)} {" ".join([f"{x} {kwargs[x]}" for x in kwargs if kwargs[x].strip()])} {limit}'
    
    rst = sql(s)
    rst.columns.name = table
    return rst

def count (table, *args, **kwargs):
    rst = select('count(*)', table, *args, **kwargs)
    return rst


from .mysqlProxy import MysqlProxy
from .magic import _setDb