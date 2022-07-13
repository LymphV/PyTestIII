'''

建立企业索引

------------

esEnterprise : 建立企业索引
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
    from .tmpIncTable.tmpEnterprises import tableTmpEnterprises, TmpEnterprises
    from .dbUtils import deleteIndexRows
else:
    from esProxy import EsProxy
    from cfg import mysqlIp, mysqlPort, mysqlUser, mysqlPassword, mysqlDb
    from utils import frmt, rmUnseen, groupConcat
    from tmpIncTable.tmpEnterprises import tableTmpEnterprises, TmpEnterprises
    from dbUtils import deleteIndexRows

from vUtil.vTime import getNow, getToday
from vUtil.vFile import fprint
from vUtil.vTqdm import tqdm, trange
from vMysql import MysqlProxy

index = 'landinn_enterprise'
indexHl = 'landinn_enterprise_highlight'

### 同企业合并不同字段时的分隔符数，防止es match_phrase时将短语分开匹配进多行中
### match_phrase的slop为10，分隔符数暂设为12
nIdSep = 12

__path__  = os.path.dirname(os.path.abspath(__file__))

def ourError (error, errorType = ''):
    path = os.path.join(__path__, 'errorEnterprise')
    fprint(f'[ERROR] ({getNow()}) {errorType} : {repr(error)}\n', file=f'error{getToday()}.txt', path=path)

def ourLog (log, logType = ''):
    path = os.path.join(__path__, 'logEnterprise')
    fprint(f'[LOG] ({getNow()}) {logType} : {repr(log)}\n', file=f'log{getToday()}.txt', path=path)

sTmpEnterprise = f'''
create temporary table tmp_enterprise
(
    select id as enterprise_id
    from {tableTmpEnterprises}
    limit %d, %d
);
'''

sTmpEnterpriseId = '''
create temporary table tmp_enterprise
(
    select affiliation_id as enterprise_id from affiliations where affiliation_id = %d
);
'''

sRmTmpEnterprise = '''
drop temporary table tmp_enterprise;
'''

sTmpPublish = '''
create temporary table tmp_publish
(
    select affiliation_id as enterprise_id, sc_id as publish_id
    from
        softwareCopyright_affiliation as a
    join
        tmp_enterprise as b
    on a.affiliation_id = b.enterprise_id
    where !ifnull(a.is_deleted, 0)
);'''

sInsertPublish = ['''
insert into tmp_publish
(
    select applicant_id as enterprise_id, patent_id as publish_id
    from
        patent_applicants as a
    join
        tmp_enterprise as b
    on a.applicant_id = b.enterprise_id
    where !ifnull(a.is_deleted, 0)
);
''',
'''
insert into tmp_publish
(
    select affiliation_id as enterprise_id, golaxy_product_id as publish_id
    from
        product as a
    join
        tmp_enterprise as b
    on a.affiliation_id = b.enterprise_id
    where !ifnull(a.is_deleted, 0)
);
''']

sRmTmpPublish = '''
drop temporary table tmp_publish;
'''

def addPublishId (x, n = nIdSep):
    if n is None:
        s = "'曓攨爩氎廤攨攡擟戅嬼壣(',publish_id,')'"
    else: s = ','.join(["'(',publish_id,')'"] * n)
    return f'''concat({s},{x})'''

def getSqlSelectData (n = nIdSep):
    return f'''
    select  enterprise_id,
            {addPublishId("softwareCopyright_name", n)} as softwareCopyright_name,
            {addPublishId("simpleName", n)} as simpleName,
            {addPublishId("patent_title", n)} as patent_title,
            {addPublishId("signory", n)} as signory,
            {addPublishId("summary", n)} as summary,
            {addPublishId("product_name", n)} as product_name,
            {addPublishId("yewu", n)} as yewu,
            {addPublishId("hangye", n)} as hangye
    from
    (
        select  enterprise_id, publish_id, softwareCopyright_name, simpleName, patent_title,
                ifnull(patent_signory, patent_signory_en) as signory,
                ifnull(patent_abstract, patent_abstract_en) as summary
        from
        (
            select enterprise_id, publish_id, softwareCopyright_name, simpleName, ifnull(patent_title, patent_title_en) as patent_title
            from
            (
                select enterprise_id, publish_id, full_name as softwareCopyright_name, simple_name as simpleName
                from tmp_publish as a
                left join software_copyright as b on a.publish_id = b.golaxy_sc_id
                where !ifnull(b.is_deleted, 0)
            ) as c
            left join patent on c.publish_id = patent.golaxy_patent_id
            where !ifnull(patent.is_deleted, 0)
        )as d
        left join patent_abstracts on d.publish_id = patent_abstracts.patent_id
        where !ifnull(patent_abstracts.is_deleted, 0)
    ) as e
    left join product on e.publish_id = product.golaxy_product_id
    where !ifnull(product.is_deleted, 0);
    '''


sSelectData = getSqlSelectData()
sSelectDataMini = getSqlSelectData(None)

sSelectInfo = '''
select  affiliation_id as enterprise_id,
        cast(not is_abroad as char) as is_chinese,
        if(official_page is null, 0, 1) as has_officialPage,
        ifnull(display_name, display_name_en) as name,
        industry,
        business_scope as businessScope,
        reg_province as province,
        reg_city as city,
        cast(reg_capital_standard as char) as regCapital,
        establishment_time as establishmentTime
from tmp_enterprise as a
join affiliations as b
on a.enterprise_id = b.affiliation_id
where !ifnull(b.is_deleted, 0);
'''



def stdData (data):
    return {
        data['enterprise_id'][i] : {
            "softwareCopyright_name" : data['softwareCopyright_name'][i],
            "simpleName" : data['simpleName'][i],
            "patent_title" : data['patent_title'][i],
            "signory" : data['signory'][i],
            "summary" : data['summary'][i],
            "product_name" : data['product_name'][i],
            "yewu" : data['yewu'][i],
            "hangye" : data['hangye'][i],
        } for i in range(len(data))
    }

def stdInfo (info):
    return {
        info['enterprise_id'][i] : {
            'is_chinese' : info['is_chinese'][i],
            'has_officialPage' : info['has_officialPage'][i],
            'name' : info['name'][i],
            'industry' : info['industry'][i],
            'businessScope' : info['businessScope'][i],
            'province' : info['province'][i],
            'city' : info['city'][i],
            'regCapital' : info['regCapital'][i],
            'establishmentTime' : info['establishmentTime'][i],
        } for i in range(len(info))
    }

def getHighLightActions (data, info):
    actions = []
    for id in info:
        action={'_op_type':'index',###操作 index update create delete
            '_index': indexHl,#index
            '_id' : str(id),
            '_source':
           {
                "enterprise_id" : str(id),
                "is_chinese" : info[id]['is_chinese'],
                "has_officialPage" : info[id]['has_officialPage'],
                "name" : info[id]['name'],
                "industry" : info[id]['industry'],
                "businessScope" : info[id]['businessScope'],
                "province" : info[id]['province'],
                "city" : info[id]['city'],
                "regCapital" : info[id]['regCapital'],
                "establishmentTime" : (None if info[id]['establishmentTime'] is pd.NaT
                                       else info[id]['establishmentTime']),
            }
        }
        actions.append(action)
    return actions

def getActions (data, info):
    actions = []
    for id in info:
        action={'_op_type':'index',###操作 index update create delete
            '_index': index,#index
            '_id' : str(id),
            '_source':
           {
                "enterprise_id" : str(id),
                "softwareCopyright_name" : data.get(id, {}).get('softwareCopyright_name', ''),
                "softwareCopyright_simpleName" : data.get(id, {}).get('simpleName', ''),
                "patent_title" : data.get(id, {}).get('patent_title', ''),
                "patent_signory" : data.get(id, {}).get('signory', ''),
                "patent_summary" : data.get(id, {}).get('summary', ''),
                "product_name" : data.get(id, {}).get('product_name', ''),
                "product_yewu" : data.get(id, {}).get('yewu', ''),
                "product_hangye" : data.get(id, {}).get('hangye', ''),
                "is_chinese" : info[id]['is_chinese'],
                "has_officialPage" : info[id]['has_officialPage'],
                "name" : info[id]['name'],
                "industry" : info[id]['industry'],
                "businessScope" : info[id]['businessScope'],
                "province" : info[id]['province'],
                "city" : info[id]['city'],
                "regCapital" : info[id]['regCapital'],
                "establishmentTime" : (None if info[id]['establishmentTime'] is pd.NaT
                                       else info[id]['establishmentTime']),
            }
        }
        actions.append(action)
    return actions

def __getData (db, mode, *args):
    while 1:
        try:
            db.sql((sTmpEnterprise if mode else sTmpEnterpriseId) % args)
            db.sql(sTmpPublish)
            for x in sInsertPublish: db.sql(x)

            data = db.sql(sSelectData if mode else sSelectDataMini)

            data = groupConcat(data, 'enterprise_id')
            info = db.sql(sSelectInfo)
            db.sql(sRmTmpEnterprise)
            db.sql(sRmTmpPublish)
            db.close()
        except pymysql.Error as e:
            ourError(str(e), 'mysql read error')
            db.close()
            continue
        break
    return stdData(data), stdInfo(info)

def getRangeData (db, now, sizeBulk):
    return __getData(db, 1, now, sizeBulk)
def getIdData (db, id):
    return __getData(db, 0, id)

def miniInsert (data, info):
    ti = tqdm(info, leave=False)
    for id in ti:
        frmt(tqdm=ti)
        actions = getActions(data, {id : info[id]})
        try:
            errorInfo = f'connetion error with id({id})'
            es.bulk(actions=actions, errorInfo=errorInfo)
        except TransportError as e:
            if 'Data too large' in str(e) or e.status_code == 413:
                ourError(str(e), f'Data too large with id({id})')
                es.restart()

                data, info = getIdData(db, id)
                actions = getActions(data, info)

                errorInfo = f'connetion error mini indexing with id({id})'
                es.bulk(actions=actions, errorInfo=errorInfo)
            else: raise e


def esEnterprise (tLast, tNow):
    es = EsProxy()
    db = MysqlProxy(ip=mysqlIp, port=mysqlPort, user=mysqlUser, password=mysqlPassword, db=mysqlDb)

    frmt('更新企业')
    deleteIndexRows(db, es, 'affiliations', 'affiliation_id', tLast=tLast, tNow=tNow, index=[index, indexHl])

    frmt('获取全部企业更新列表', end='\r')
    tmpEnterprises = TmpEnterprises(db)
    tmpEnterprises.start(tLast, tNow)

    sizeBulk = 5
    now = 0
    nEnterprise = len(tmpEnterprises)
    db.close()

    frmt(f'获取全部企业更新列表({nEnterprise})')
    ourLog(nEnterprise, '获取全部企业更新列表')
    tr = trange(now, nEnterprise, sizeBulk)
    for i in tr:
        frmt(tqdm=tr)
        now = i ### 在测试时为方便断点续传

        data, info = getRangeData(db, now, sizeBulk)

        errorInfo =  f'connetion error indexing hl with Range({now},{now + sizeBulk})'
        es.bulk(actions=getHighLightActions(data,info), errorInfo=errorInfo)

        actions = getActions(data, info)

        try:
            errorInfo = f'connetion error with Range({now},{now + sizeBulk})'
            es.bulk(actions=actions, errorInfo=errorInfo)
        except TransportError as e:
            if 'Data too large' in str(e) or e.status_code == 413:
                ourError(str(e), f'Data too large with Range({now},{now + sizeBulk})')
                es.restart()
                miniInsert (data, info)
            else: raise e

        ourLog([*info], f'更新企业索引({len(info)})')

    tmpEnterprises.close()
    es.close()
    db.close()
