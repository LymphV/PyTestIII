'''

建立索引基类

-----------


EsBase : 建立索引的基类
EsMainBase : 建立学者/企业索引的基类
'''

import os, sys, re, json
from elasticsearch import TransportError

from .cfg import mysqlDb

from .dbUtils import deleteIndexRows
from .tmpIncTable.viewAll import ViewAll

from vEs import EsProxy
from vUtil.vTime import getNow, getToday
from vUtil.vFile import fprint
from vUtil.vTqdm import tqdm, trange
from vMysql import MysqlProxy
from vUtil.vLog import frmt
from vGlobals import vGlobals

__path__  = os.path.dirname(os.path.abspath(__file__))

vGlobals.timeManagerType = ''

class EsBase:
    '''
    建立索引的基类

    需要挂载成员
        getData : callable,
        getActions : callable,
        sizeBulk : int
        hasIsNew : bool
    并实现成员函数
        self._es(db, es, tableTmp, now, tLast, tNow)
    '''
    __version__ = 20220613
    __author__ = 'LymphV@163.com'

    def __init__ (self, this, thisEn, table, idCol, index, Tmp):
        self.this = this
        self.thisEn = thisEn
        self.table = table
        self.idCol = idCol
        self.index = index
        self.indexes = [index]
        self.Tmp = Tmp
        self.getData = None
        self.getActions = None
        self.sizeBulk = None
        self.hasIsNew = False
        self.isAbroad = None

    def ourError (self, error, errorType = ''):
        path = os.path.join(__path__, f'error{vGlobals.timeManagerType}/{self.thisEn}')
        fprint(f'[ERROR] ({getNow()}) {errorType} : {repr(error)}', file=f'error{getToday()}.txt', path=path)

    def ourLog (self, log, logType = ''):
        path = os.path.join(__path__, f'log{vGlobals.timeManagerType}/{self.thisEn}')
        fprint(f'[LOG] ({getNow()}) {logType} : {repr(log)}', file=f'log{getToday()}.txt', path=path)

    def __call__ (self, tLast, tNow):
        es = EsProxy()
        db = MysqlProxy(db=mysqlDb)

        frmt(f'获取全部{self.this}更新列表', end='\r')
        tmp = ViewAll(
            db, self.thisEn, self.table, self.idCol, self.hasIsNew, self.isAbroad
        ) if tLast is None and tNow is None else self.Tmp(db)
        
        try:
            tmp.start(tLast, tNow)
            tableTmp = tmp.tableTmp

            sizeBulk = self.sizeBulk
            now = 0
            nThis = len(tmp)
            db.close()

            frmt(f'获取全部{self.this}更新列表({nThis})', end='\r')
            self.ourLog(nThis, f'获取全部{self.this}更新列表')
            if nThis:
                lastId = -1
                with trange(now, nThis, sizeBulk) as tr:
                    for i in tr:
                        frmt(self.this, f'{i}/{nThis}', tqdm=tr)
                        now = i ### 在测试时为方便断点续传

                        lastId = self._es(db, es, tableTmp, now, tLast, tNow, lastId)
                self.ourLog('-' * 20)
            deleteIndexRows(db, es, self.table, self.idCol, tLast=tLast, tNow=tNow,
                index=self.indexes, this=self.this, hasIsNew=self.hasIsNew)
        finally:
            tmp.close()
            es.close()
            db.close()

    def _es (self, db, es, tableTmp, now, tLast, tNow, lastId):
        data = self.getData(db, tableTmp, now, self.sizeBulk, lastId)

        actions = self.getActions(*data, self.index)
        rst = max(int(x['_id']) for x in actions)

        errorInfo = f'connetion error indexing {self.thisEn} Time({tLast},{tNow}) Range({now},{now + self.sizeBulk})'
        if actions: es.bulk(actions=actions, errorInfo=errorInfo)

        data, *_ = data
        self.ourLog([*data['gid']], f'更新{self.this}索引({len(data["gid"])})')
        return rst

class EsMainBase(EsBase):
    '''
    建立学者/企业索引的基类

    需要挂载成员
        getData : callable,
        getActions : callable,
        getHighLightActions : callable,
        sizeBulk : int
    '''
    __version__ = 20210727
    __author__ = 'LymphV@163.com'

    def __init__ (self, this, thisEn, table, idCol, index, indexHl, Tmp, isAbroad=None):
        EsBase.__init__(self, this, thisEn, table, idCol, index, Tmp)
        self.indexHl = indexHl
        self.indexes = [index, indexHl]
        self.getHighLightActions = None
        self.hasIsNew = True
        self.isAbroad = isAbroad

    def miniInsert (self, db, es, data, info):
        '''
        间隔符导致内容过长时，先尝试逐个索引，后尝试使用生僻字做间隔符
        '''
        with tqdm(info, leave=False) as ti:
            for id in ti:
                frmt('mini insert', tqdm=ti)
                actions = self.getActions(data, {id : info[id]}, self.index)
                try:
                    errorInfo = f'connetion error with {self.thisEn} id({id})'
                    es.bulk(actions=actions, errorInfo=errorInfo)
                except TransportError as e:
                    if 'Data too large' in str(e) or e.status_code == 413:
                        self.ourError(repr(e), f'Data too large with {self.thisEn} id({id})')
                        es.restart()

                        data, info = self.getData.getIdData(db, id)
                        actions = self.getActions(data, info, self.index)

                        errorInfo = f'connetion error mini indexing with {self.thisEn} id({id})'
                        es.bulk(actions=actions, errorInfo=errorInfo)
                    else: raise e

    def _es (self, db, es, tableTmp, now, tLast, tNow, lastId):
        sizeBulk = self.sizeBulk
        data, info = self.getData.getRangeData(db, tableTmp, now, sizeBulk, lastId)

        actions = self.getHighLightActions(data, info, self.indexHl)
        rst = max(int(x['_id']) for x in actions)

        errorInfo = f'connetion error indexing {self.thisEn} hl Time({tLast},{tNow}) with Range({now},{now + sizeBulk})'
        es.bulk(actions=actions, errorInfo=errorInfo)

        actions = self.getActions(data, info, self.index)

        try:
            errorInfo = f'connetion error with {self.thisEn} Time({tLast},{tNow}) Range({now},{now + sizeBulk})'
            es.bulk(actions=actions, errorInfo=errorInfo)
        except TransportError as e:
            if 'Data too large' in str(e) or e.status_code == 413:
                self.ourError(repr(e), f'Data too large with {self.thisEn} Time({tLast},{tNow}) Range({now},{now + sizeBulk})')
                es.restart()
                self.miniInsert (db, es, data, info)
            else: raise e

        self.ourLog([*info], f'更新{self.this}索引({len(info)})')
        return rst
