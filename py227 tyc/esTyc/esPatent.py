'''

建立专利索引

------------

esPatent : 建立专利索引
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
    from .tmpIncTable.tmpPatents import tableTmpPatents, TmpPatents
    from .dbUtils import deleteIndexRows
else:
    from esProxy import EsProxy
    from cfg import mysqlIp, mysqlPort, mysqlUser, mysqlPassword, mysqlDb
    from utils import frmt, rmUnseen, groupConcat
    from tmpIncTable.tmpPatents import tableTmpPatents, TmpPatents
    from dbUtils import deleteIndexRows



from vUtil.vTime import getNow, getToday
from vUtil.vFile import fprint
from vUtil.vTqdm import tqdm, trange
from vMysql import MysqlProxy

index = 'landinn_patent'

__path__  = os.path.dirname(os.path.abspath(__file__))

def ourError (error, errorType = ''):
    path = os.path.join(__path__, 'errorPatent')
    fprint(f'[ERROR] ({getNow()}) {errorType} : {repr(error)}\n', file=f'error{getToday()}.txt', path=path)

def ourLog (log, logType = ''):
    path = os.path.join(__path__, 'logPatent')
    fprint(f'[LOG] ({getNow()}) {logType} : {repr(log)}\n', file=f'log{getToday()}.txt', path=path)

sTmpPatent = f'''
create temporary table tmp_patent
(
    select  golaxy_patent_id as gid,
            ifnull(patent_title, patent_title_en) as title,
            applicant_date,
            grant_date,
            publication_date
    from
    patent as a
    join
    (
        select id from {tableTmpPatents}
        limit %d, %d
    ) as b
    on a.golaxy_patent_id = b.id
    where !ifnull(a.is_deleted, 0)
);
'''

sRmTmpPatent = '''
drop temporary table tmp_patent;
'''

sSelectPublishScholar = '''
select gid, cast(author_id as char) as scholar_id, null as enterprise_id
from
    tmp_patent as a
left join patent_authors as b
on a.gid = b.patent_id
where !ifnull(b.is_deleted,0);
'''

sSelectPublishEnterprise = '''
select gid, null as scholar_id, cast(applicant_id as char) as enterprise_id
from
    tmp_patent as c
left join patent_applicants as d
on c.gid = d.patent_id
where !ifnull(d.is_deleted,0);
'''


sSelectData = '''
select  gid, title, applicant_date, grant_date, publication_date,
        ifnull(patent_signory, patent_signory_en) as signory,
        ifnull(patent_abstract, patent_abstract_en) as summary
from
    tmp_patent as a
left join patent_abstracts as b on a.gid = b.patent_id
where !ifnull(b.is_deleted, 0)
;
'''

def getActions (data, publish):
    actions = []

    p2s = {publish['gid'][i] : publish['scholar_id'][i] for i in range(len(publish))}
    p2e = {publish['gid'][i] : publish['enterprise_id'][i] for i in range(len(publish))}

    for i in range(len(data)):
        if data['gid'][i] not in p2s: continue
        action={'_op_type':'index',#操作 index update create delete
            '_index':index,#index
            '_id' : data['gid'][i],
            '_source':
           {
                "id" : data['gid'][i],
                "title" : rmUnseen(data['title'][i], None),
                "signory" : rmUnseen(data['signory'][i], None),
                "summary" : rmUnseen(data['summary'][i], None),
                "scholars" : p2s[data['gid'][i]],
                "enterprises" : p2e[data['gid'][i]],
                "applicant_date" : None if data['applicant_date'][i] is pd.NaT else data['applicant_date'][i],
                "grant_date" : None if data['grant_date'][i] is pd.NaT else data['grant_date'][i],
                "publication_date" : None if data['publication_date'][i] is pd.NaT else data['publication_date'][i]
            }
        }
        actions.append(action)
    return actions

def esPatent (tLast, tNow):
    es = EsProxy()
    db = MysqlProxy(ip=mysqlIp, port=mysqlPort, user=mysqlUser, password=mysqlPassword, db=mysqlDb)

    frmt('更新专利')
    deleteIndexRows(db, es, 'patent', 'golaxy_patent_id', tLast=tLast, tNow=tNow, index=index)

    frmt('获取全部专利更新列表', end='\r')
    tmpPatents = TmpPatents(db)
    tmpPatents.start(tLast, tNow)

    sizeBulk = 100
    now = 0
    nPatent = len(tmpPatents)
    db.close()

    frmt(f'获取全部专利更新列表({nPatent})')
    ourLog(nPatent, '获取全部专利更新列表')
    tr = trange(now, nPatent, sizeBulk)
    for i in tr:
        frmt(tqdm=tr)
        now = i ### 在测试时为方便断点续传

        db.sql(sTmpPatent % (now, sizeBulk))

        data = db.sql(sSelectData)
        ps = db.sql(sSelectPublishScholar)
        pe = db.sql(sSelectPublishEnterprise)
        publish = ps.append(pe, ignore_index=True)
        db.sql(sRmTmpPatent)
        db.close()

        actions = getActions(data, groupConcat(publish, 'gid', ';'))
        errorInfo = f'connetion error indexing patent Time({tLast},{tNow}) Range({now},{now + sizeBulk})'
        if actions: es.bulk(actions=actions, errorInfo=errorInfo)

        ourLog([*data['gid']], f'更新产品索引({len(data["gid"])})')

    tmpPatents.close()
    es.close()
    db.close()
