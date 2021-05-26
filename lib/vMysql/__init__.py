import pandas as pd

dbs = []
def addDb (db):
    dbs.append(db)


def sql(s):
    cursor = dbs[-1].cursor()
    cursor.execute(s)
    rst = cursor.fetchall()
    
    rst = pd.DataFrame(rst, columns=[*zip(*cursor.description)][0] if cursor.description else [])
    return rst

def describe (table):
    rst = sql(f'describe {table};')
    rst.columns.name = table
    return rst

def select (items, table, *args, **kwargs):
    def deal (s):
        s = str(s).strip()
        return f'`{s}`' if s.isalnum() else s
    
    
    if type(items) is str:
        items = items.split(',')
    item = ','.join([deal(x) for x in items])
        
    if args:
        r = range(*args)
        start, stop = r.start, r.stop
        limit = f'limit {start}, {stop - start}'
    else: limit = ''
    
    s = f'select {item} from {deal(table)} {" ".join([f"{x} {kwargs[x]}" for x in kwargs if kwargs[x].strip()])} {limit}'
    
    rst = sql(s)
    rst.columns.name = table
    return rst

def count (table, *args, **kwargs):
    rst = select('count(*)', table, *args, **kwargs)
    return rst


from .MysqlProxy import MysqlProxy