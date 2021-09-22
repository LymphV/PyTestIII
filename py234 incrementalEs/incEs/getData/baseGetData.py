
import pandas as pd
import os, re, sys, json
import pymysql

from vUtil.vLog import frmt, VError, VLog, rootPath
from vUtil.debug import debug
from vGlobals import vGlobals

__path__  = os.path.dirname(os.path.abspath(__file__))

vGlobals.timeManagerType = ''
vGlobals.ourError = VError(path=os.path.join(rootPath, f'error{vGlobals.timeManagerType}'))
vGlobals.ourLog = VLog(path=os.path.join(rootPath, f'log{vGlobals.timeManagerType}'))

def addPublishId (x, n):
    if n is None:
        s = "'曓攨爩氎廤攨攡擟戅嬼壣(',publish_id,')'"
    else: s = ','.join(["'(',publish_id,')'"] * n)
    return f'''concat({s},{x})'''

def rmUnseen (s, none = ''):
    '''
    去除不可见字符
    '''
    if s is None: return none
    return re.sub(r'\s+', ' ', str(s))

def groupConcat (data, field = 'scholar_id', sep = '\n'):
    return pd.DataFrame([
        [x] +
        [
            sep.join([rmUnseen(data[j][i]) for i in range(len(data)) if data[field][i] == x and data[j][i]])
            for j in data if j != field
        ] for x in sorted(set(data[field]))
    ], columns = [*data])

class BaseGetData:
    '''
    需实现成员函数
        self._getData(db, *args)
    '''
    def __init__ (self, this, thisEn, table, idCol):
        self.this = this
        self.thisEn = thisEn
        self.table = table
        self.idCol = idCol

        self.sRmTmp = f'drop temporary table tmp_{thisEn};'

    def __call__ (self, db, *args, **kw):
        '''
        获取数据
        参数同self._getData
        '''
        while 1:
            try:
                rst = self._getData(db, *args, **kw)
                return rst
            except pymysql.Error as e:
                vGlobals.ourError(f'({debug.file}:{debug.lineno})', 'mysql read error',
                    repr(e), f'\nhistory="""{db.history}"""')
                db.close()


class MainGetData(BaseGetData):
    '''
    获取学者/企业数据

    ----------------
    self.getRangeData : 获取范围数据
    self.getIdData : 获取指定id数据

    ---------
    需
        挂载成员
            sTmpPublish : sql,
            sInsertPublish : [sql],
            sSelectData : sql,
            sSelectDataMini : sql,
            sSelectInfo : sql,
        实现成员函数
            self.stdData(data:pd.DataFrame)
            self.stdInfo(info:pd.DataFrame)
    '''
    def __init__ (self, this, thisEn, table, idCol):
        BaseGetData.__init__(self, this, thisEn, table, idCol)

        self.sTmp = f'''
        create temporary table tmp_{thisEn}
        (
            select id as {thisEn}_id from %s
            where id > %d order by id
            limit %d
        );
        '''

        self.sTmpId = f'''
        create temporary table tmp_{thisEn}
        (
            select {idCol} as {thisEn}_id from {table} where {idCol} = %d
        );
        '''

        self.sRmTmpPublish = 'drop temporary table tmp_publish;'

    def _getData (self, db, mode, *args):
        db.sql((self.sTmp if mode else self.sTmpId) % args, ifCommit=1, ifRetry=0)
        db.sql(self.sTmpPublish, ifCommit=1, ifRetry=0)
        for x in self.sInsertPublish: db.sql(x, ifCommit=1, ifRetry=0)

        data = db.sql(self.sSelectData if mode else self.sSelectDataMini, ifCommit=1, ifRetry=0)

        info = db.sql(self.sSelectInfo, ifCommit=1, ifRetry=0)
        db.sql(self.sRmTmp, ifCommit=1, ifRetry=0)
        db.sql(self.sRmTmpPublish, ifCommit=1, ifRetry=0)
        db.close()

        data = groupConcat(data, f'{self.thisEn}_id')
        return self.stdData(data), self.stdInfo(info)

    def getRangeData (self, db, tableTmp, now, sizeBulk, lastId=-1):
        '''
        获取范围数据

        Parameters
        ----------
        db : MySQLProxy，数据库连接
        tableTmp : 临时表名
        now : 当前偏移量
        sizeBulk : bulk大小
        '''
        return self(db, 1, tableTmp, lastId, sizeBulk)

    def getIdData (self, db, id):
        '''
        获取指定id数据

        Parameters
        ----------
        db : MySQLProxy，数据库连接
        id : 指定id
        '''
        return self(db, 0, id)
