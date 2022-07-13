

import pymysql
import pandas as pd
from time import sleep

from vUtil.vLog import vError

from .password import mysqlIp, mysqlPort, mysqlUser, mysqlPassword, mysqlDb
from .utils import stdSqlData, stdSqlCol
from .cfg import codeErr as dftCodeErr, maxErr as dftMaxErr


class MysqlProxy:
    '''
    mysql代理
    '''
    
    __version__ = 20220331
    __author__ = 'LymphV@163.com'
    
    def __init__ (this, ip=mysqlIp, port=mysqlPort, user=mysqlUser, password=mysqlPassword, db=mysqlDb, codeErr=dftCodeErr, maxErr=dftMaxErr):
        '''
        mysql代理
        '''
        this.__db =None
        this.ip = ip
        this.port = port
        this.user = user
        this.password = password
        this.database = db
        this.history = None
        this.start()
        
        this.codeErr = codeErr or dftCodeErr
        this.maxErr = maxErr or dftMaxErr
    
    def __str__ (this):
        data = {'host' : this.ip, 'port' : this.port, 'user' : this.user}
        return f'<vMysql.MysqlProxy({data})>'
    
    def __repr__ (this):
        return str(this)
    
    def start (this):
        if pymysql.__version__ < '1':
            this.__db = pymysql.connect(this.ip, this.user, this.password,port=this.port,charset='utf8mb4',db=this.database)
        else:
            this.__db = pymysql.connect(host=this.ip, user=this.user, password=this.password,port=this.port,charset='utf8mb4',database=this.database)
    def close (this):
        if this.__db: 
            try:
                this.__db.close()
            except pymysql.Error: pass
        #this.__db = None
    
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
    
    def sql(this, s, ifCommit=False, ifRetry=True):
        '执行sql语句'
        this.history = s
        
        i = 1
        while 1:
            cursor = None
            try:
                db = this.db
                cursor = db.cursor()
                cursor.execute(s)
                rst = cursor.fetchall()
                
                rst = pd.DataFrame(rst, columns=[*zip(*cursor.description)][0] if cursor.description else [])
                
                if ifCommit: db.commit()
                break
            except pymysql.err.Error as e:
                vError(repr(e))
                code = e.args[0]
                ### 不重试、重试无效的错误码、错误最大次
                if not ifRetry or code in this.codeErr or this.maxErr <= i: raise e
                sleep(1)
                i += 1
            finally:
                if cursor is not None: cursor.close()
        return rst
    
    __call__ = sql
    
    def show (this, sth='schemas', ifCommit=True, ifRetry=True, **kwargs):
        'show'
        s = f'show {sth} {" ".join([f"{x} {kwargs[x]}" for x in kwargs if kwargs[x].strip()])};'
        rst = this(s, ifCommit=ifCommit, ifRetry=ifRetry)
        rst.columns.name = sth
        return rst
    
    def describe (this, table, ifCommit=True, ifRetry=True):
        '表描述'
        rst = this.sql(f'describe {table};', ifCommit=ifCommit, ifRetry=ifRetry)
        rst.columns.name = table
        return rst

    def select (this, items, table, *args, ifCommit=True, ifRetry=True, **kwargs):
        'select 语句'
        
        if type(items) is str:
            items = items.split(',')
        item = ','.join([stdSqlCol(x) for x in items])
            
        if args:
            r = range(*args)
            start, stop = r.start, r.stop
            limit = f'limit {start}, {stop - start}'
        else: limit = ''
        
        s = f'select {item} from {stdSqlCol(table)} {" ".join([f"{x} {kwargs[x]}" for x in kwargs if kwargs[x].strip()])} {limit};'
        
        rst = this.sql(s, ifCommit=ifCommit, ifRetry=ifRetry)
        rst.columns.name = table
        return rst

    def count (this, table, *args, ifCommit=True, ifRetry=True, **kwargs):
        '计数'
        rst = this.select('count(*)', table, *args, ifCommit=ifCommit, ifRetry=ifRetry, **kwargs)
        return rst
    
    def insert (this, table, *args, df=None, ifCommit=True, ifRetry=True, ignore=False, replace=False, **kwargs):
        '''
        插入
        
        *args为顺序数据库字段，**kwargs为指定数据库字段，df为dataFrame类型，不同时生效，优先使用顺序为*args、**kwargs、df
        
        若指定字段与已有参数名相同则建议使用**{'`table`' : None}的形式传参
        '''
        if len(args) == 0 and len(kwargs) == 0 and (not isinstance(df, pd.DataFrame) or len(df) == 0): return
        
        if replace: ignore = False
        ignore = ' ignore' if ignore else ''
        replace = 'replace' if replace else 'insert'
        
        if len(args):
            s = f'''
                {replace}{ignore} into {table} values %s;
            '''
            value = '(' + ','.join([stdSqlData(x,db=this.__db) for x in args]) + ')'
            return this.sql(s % value, ifCommit=ifCommit, ifRetry=ifRetry)
        
        if len(kwargs):
            col, value = [*zip(*kwargs.items())]
            col = '(' + ','.join(stdSqlCol(x) for x in col) + ')'
            value = '(' + ','.join(stdSqlData(x,db=this.__db) for x in value) + ')'
        else:        
            col = '(' + ','.join(stdSqlCol(x) for x in df) + ')'
            values = [
                '(' + ','.join(stdSqlData(df[x][i],db=this.__db) for x in df) + ')'
                for i in range(len(df))
            ]
            value = ','.join(values)
        s = f'''
            {replace}{ignore} into {table} %s values %s;
        '''
        return this.sql(s % (col, value), ifCommit=ifCommit, ifRetry=ifRetry)
        
    
    def stdSqlData (this, s):
        return stdSqlData(s, this.__db)
    
    def stdSqlDataRemain (this, s):
        return stdSqlData(s, this.__db, True)
    
    def stdSqlCol (this, s):
        return stdSqlCol(s)
    
    def sInSet (this, values):
        values = [this.stdSqlDataRemain(x) for x in set(values)]
        s = ','.join(values)
        return f'''({s})'''
    
    def __getattr__ (this, name):
        return this.db.__getattribute__(name)