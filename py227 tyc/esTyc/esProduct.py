'''

建立产品索引

------------

esProduct : 建立产品索引
'''

from elasticsearch import helpers
import pymysql

import json
import re
import numpy as np
import pandas as pd
import os
from time import time, sleep
import sys

if '.' in __name__:
    from .esProxy import EsProxy
    from .cfg import mysqlIp, mysqlPort, mysqlUser, mysqlPassword, mysqlDb
    from .utils import frmt, rmUnseen, groupConcat
    from .tmpIncTable.tmpProducts import tableTmpProducts, TmpProducts
    from .dbUtils import deleteIndexRows
else:
    from esProxy import EsProxy
    from cfg import mysqlIp, mysqlPort, mysqlUser, mysqlPassword, mysqlDb
    from utils import frmt, rmUnseen, groupConcat
    from tmpIncTable.tmpProducts import tableTmpProducts, TmpProducts
    from dbUtils import deleteIndexRows



from vUtil.vTime import getNow, getToday
from vUtil.vFile import fprint
from vUtil.vTqdm import tqdm, trange
from vMysql import MysqlProxy

index = 'landinn_product'


__path__  = os.path.dirname(os.path.abspath(__file__))

def ourError (error, errorType = ''):
    path = os.path.join(__path__, 'errorProduct')
    fprint(f'[ERROR] ({getNow()}) {errorType} : {repr(error)}\n', file=f'error{getToday()}.txt', path=path)

def ourLog (log, logType = ''):
    path = os.path.join(__path__, 'logProduct')
    fprint(f'[LOG] ({getNow()}) {logType} : {repr(log)}\n', file=f'log{getToday()}.txt', path=path)

sTmpProduct = f'''
create temporary table tmp_product
(
    select golaxy_product_id as gid, product_name as name, hangye, yewu, setup_time,
        cast(affiliation_id as char) as enterprises
    from
    product as a
    join
    (
        select id from {tableTmpProducts}
        limit %d, %d
    ) as b
    on a.golaxy_product_id = b.id
    where !ifnull(a.is_deleted, 0)
);
'''
sRmTmpProduct = '''
drop temporary table tmp_product;
'''

sSelectData = '''
select  gid, name, hangye, yewu, setup_time, enterprises
from tmp_product;
'''


def getActions (data):
    actions = []
    for i in range(len(data)):
        action={'_op_type':'index',#操作 index update create delete
            '_index':index,#index
            '_id' : data['gid'][i],
            '_source':
           {
                "id" : data['gid'][i],
                "name" : rmUnseen(data['name'][i], None),
                "yewu" : rmUnseen(data['yewu'][i], None),
                "hangye" : rmUnseen(data['hangye'][i], None),
                "enterprises" : data['enterprises'][i],
                "setup_time" : None if data['setup_time'][i] is pd.NaT else data['setup_time'][i],
            }
        }
        actions.append(action)
    return actions


def esProduct(tLast, tNow):
    es = EsProxy()
    db = MysqlProxy(ip=mysqlIp, port=mysqlPort, user=mysqlUser, password=mysqlPassword, db=mysqlDb)

    frmt('更新产品')
    deleteIndexRows(db, es, 'product', 'golaxy_product_id', tLast=tLast, tNow=tNow, index=index)

    frmt('获取全部产品更新列表', end='\r')
    tmpProducts = TmpProducts(db)
    tmpProducts.start(tLast, tNow)

    sizeBulk = 100
    now = 0
    nProduct = len(tmpProducts)
    db.close()

    frmt(f'获取全部产品更新列表({nProduct})')
    ourLog(nProduct, '获取全部产品更新列表')
    tr = trange(now, nProduct, sizeBulk)
    for i in tr:
        frmt(tqdm=tr)
        now = i ### 在测试时为方便断点续传

        db.sql(sTmpProduct % (now, sizeBulk))

        data = db.sql(sSelectData)
        db.sql(sRmTmpProduct)
        db.close()

        actions = getActions(data)
        errorInfo = f'connetion error indexing product Time({tLast},{tNow}) Range({now},{now + sizeBulk})'
        if actions: es.bulk(actions=actions, errorInfo=errorInfo)

        ourLog([*data['gid']], f'更新产品索引({len(data["gid"])})')

    tmpProducts.close()
    es.close()
    db.close()
