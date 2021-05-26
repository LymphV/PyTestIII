

import pymysql
import pandas as pd

from .cfg import mysqlIp, mysqlPort, mysqlUser, mysqlPassword, mysqlDb


class MysqlProxy:
    '''
    mysql代理
    '''
    
    __version__ = 20210517
    __author__ = 'LymphV@163.com'
    
    def __init__ (this, ip=mysqlIp, port=mysqlPort, user=mysqlUser, password=mysqlPassword, db=mysqlDb):
        '''
        mysql代理
        '''
        this.__db =None
        this.ip = ip
        this.port = port
        this.user = user
        this.password = password
        this.database = db
        this.start()
    def start (this):
        if pymysql.__version__ < '1':
            this.__db = pymysql.connect(this.ip, this.user, this.password,port=this.port,charset='utf8mb4',db=this.database)
        else:
            this.__db = pymysql.connect(host=this.ip, user=this.user, password=this.password,port=this.port,charset='utf8mb4',database=this.database)
    def close (this):
        if this.__db: this.__db.close()
        this.__db = None
    
    @property
    def db (this):
        '''
        db的getter函数
        
        若无效或失去连接将自动重新连接
        '''
        if this.__db is None: this.start()
        this.__db.ping()
        return this.__db
    
    def commit(this):
        this.db.commit()
    
    def sql(this, s, ifCommit=False):
        '执行sql语句'
        db = this.db
        cursor = db.cursor()
        cursor.execute(s)
        rst = cursor.fetchall()
        
        rst = pd.DataFrame(rst, columns=[*zip(*cursor.description)][0] if cursor.description else [])
        
        if ifCommit: db.commit()
        return rst
    
    def describe (this, table):
        '表描述'
        rst = this.sql(f'describe {table};')
        rst.columns.name = table
        return rst

    def select (this, items, table, *args, **kwargs):
        'select 语句'
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
        
        s = f'select {item} from {deal(table)} {" ".join([f"{x} {kwargs[x]}" for x in kwargs if kwargs[x].strip()])} {limit};'
        
        rst = this.sql(s)
        rst.columns.name = table
        return rst

    def count (this, table, *args, **kwargs):
        '计数'
        rst = this.select('count(*)', table, *args, **kwargs)
        return rst