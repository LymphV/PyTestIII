import re, os
import pandas as pd

from vUtil.vTime import getNow
from vUtil.vTqdm import tqdm, trange
from vUtil.vLog import frmt, VLog, VError
from vMysql import stdSqlData
from vGlobals import vGlobals

__path__  = os.path.dirname(os.path.abspath(__file__))

vGlobals.timeManagerType = ''
vGlobals.ourError = VError(path=os.path.join(__path__, '..', f'error{vGlobals.timeManagerType}'))
vGlobals.ourLog = VLog(path=os.path.join(__path__, '..', f'log{vGlobals.timeManagerType}'))

delSizeBulk = 1000

def deleteIndexRows (db, es, table, idCol, tLast=None, tNow=None, hasIsNew=False, where=None, index=None, this=''):
    '''
    删除索引行
    移除数据库中废除的行对应的es索引

    Parameters
    ----------
    db : mysql数据库连接，MysqlProxy对象
    es : es连接，有delete_by_query函数
    table : 检验废除行的数据库表
    idCol : 数据库表的id列
    where : 除is_deleted废除标记以外的筛选条件
    index : 需要移除废除行的es索引表名，str或str组成的list
    '''
    if index is None: return
    if isinstance(index, str): index = [index]

    isDeleted = 'ifnull(is_deleted,0)'
    isNew = 'ifnull(is_new,0)' if hasIsNew else ''

    where = [
        f'({isDeleted} or {isNew})' if hasIsNew else isDeleted,
        (f'{stdSqlData(tLast)} <= ifnull (updated_at, created_at)' if tLast else ''),
        (f'ifnull (updated_at, created_at) < {stdSqlData(tNow)}' if tNow else ''),
        (f'({where})' if where else ''),
    ]
    where = '\n\tand '.join([x for x in where if x])

    nDel = db.count(table, where=where).values.item()
    db.close()

    tot = {x : 0 for x in index}
    if not nDel: return tot
    with trange(0, nDel, delSizeBulk) as tr:
        for i in tr:
            frmt(f'移除新增{this}删除{i}/{nDel}', tqdm=tr)
            ids = db.select(idCol, table, i, i + delSizeBulk, where=where)[idCol]

            db.close()

            ids = [str(x) for x in ids]
            for x in index:
                nDeleted = es.delete_by_query(index=x, body = {
                    "query": {
                        "terms": {"_id": ids}
                    }
                }).get('deleted', 0)
                tot[x] += nDeleted
                vGlobals.ourLog(f'删除{x}索引({nDeleted})', ids)
    return tot
