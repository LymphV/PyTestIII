'''

建立软著索引

------------

esSoftwareCopyright : 建立软著索引
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
    from .tmpIncTable.tmpSoftwareCopyrights import tableTmpSoftwareCopyrights, TmpSoftwareCopyrights
    from .dbUtils import deleteIndexRows
else:
    from esProxy import EsProxy
    from cfg import mysqlIp, mysqlPort, mysqlUser, mysqlPassword, mysqlDb
    from utils import frmt, rmUnseen, groupConcat
    from tmpIncTable.tmpSoftwareCopyrights import tableTmpSoftwareCopyrights, TmpSoftwareCopyrights
    from dbUtils import deleteIndexRows

from vUtil.vTime import getNow, getToday
from vUtil.vFile import fprint
from vUtil.vTqdm import tqdm, trange
from vMysql import MysqlProxy

index = 'landinn_software_copyright'

__path__  = os.path.dirname(os.path.abspath(__file__))

def ourError (error, errorType = ''):
    path = os.path.join(__path__, 'errorSoftwareCopyright')
    fprint(f'[ERROR] ({getNow()}) {errorType} : {repr(error)}\n', file=f'error{getToday()}.txt', path=path)

def ourLog (log, logType = ''):
    path = os.path.join(__path__, 'logSoftwareCopyright')
    fprint(f'[LOG] ({getNow()}) {logType} : {repr(log)}\n', file=f'log{getToday()}.txt', path=path)

sTmpSoftwareCopyright = f'''
create temporary table tmp_softwareCopyright
(
    select  golaxy_sc_id as gid,
            full_name as name,
            simple_name as simpleName,
            registration_time,
            publish_time,
            event_time
    from
    software_copyright as a
    join
    (
        select id from {tableTmpSoftwareCopyrights}
        limit %d, %d
    ) as b
    on a.golaxy_sc_id = b.id
    where !ifnull(a.is_deleted, 0)
);
'''

sRmTmpSoftwareCopyright = '''
drop temporary table tmp_softwareCopyright;
'''


sSelectPublish = '''
select gid, cast(affiliation_id as char) as enterprise_id
from
    tmp_softwareCopyright as a
left join softwareCopyright_affiliation as b
on a.gid = b.sc_id
where !ifnull(b.is_deleted, 0);
'''

sSelectData = '''
select gid, name, simpleName, registration_time, publish_time, event_time
from tmp_softwareCopyright;
'''

def getActions (data, publish):
    actions = []

    p2e = {publish['gid'][i] : publish['enterprise_id'][i] for i in range(len(publish))}

    for i in range(len(data)):
        action={'_op_type':'index',#操作 index update create delete
            '_index':index,#index
            '_id' : data['gid'][i],
            '_source':
           {
                "id" : data['gid'][i],
                "name" : rmUnseen(data['name'][i], None),
                "simpleName" : rmUnseen(data['simpleName'][i], None),
                "enterprises" : p2e[data['gid'][i]],
                "registration_time" : None if data['registration_time'][i] is pd.NaT else data['registration_time'][i],
                "publish_time" : None if data['publish_time'][i] is pd.NaT else data['publish_time'][i],
                "event_time" : None if data['event_time'][i] is pd.NaT else data['event_time'][i],
            }}
        actions.append(action)
    return actions

def esSoftwareCopyright (tLast, tNow):
    es = EsProxy()
    db = MysqlProxy(ip=mysqlIp, port=mysqlPort, user=mysqlUser, password=mysqlPassword, db=mysqlDb)

    frmt('更新软著')
    deleteIndexRows(db, es, 'software_copyright', 'golaxy_sc_id', tLast=tLast, tNow=tNow, index=index)

    frmt('获取全部软著更新列表', end='\r')
    tmpSoftwareCopyrights = TmpSoftwareCopyrights(db)
    tmpSoftwareCopyrights.start(tLast, tNow)

    sizeBulk = 100
    now = 0
    nSoftwareCopyright = len(tmpSoftwareCopyrights)
    db.close()

    frmt(f'获取全部软著更新列表({nSoftwareCopyright})')
    ourLog(nSoftwareCopyright, '获取全部软著更新列表')
    tr = trange(now, nSoftwareCopyright, sizeBulk)
    for i in tr:
        frmt(tqdm=tr)
        now = i ### 在测试时为方便断点续传
        db.sql(sTmpSoftwareCopyright % (now, sizeBulk))

        data = db.sql(sSelectData)
        publish = db.sql(sSelectPublish)
        db.sql(sRmTmpSoftwareCopyright)
        db.close()

        actions = getActions(data, groupConcat(publish, 'gid', ';'))
        errorInfo = f'connetion error indexing softwareCopyright Time({tLast},{tNow}) Range({now},{now + sizeBulk})'
        if actions: es.bulk(actions=actions, errorInfo=errorInfo)

        ourLog([*data['gid']], f'更新软著索引({len(data["gid"])})')

    tmpSoftwareCopyrights.close()
    es.close()
    db.close()
