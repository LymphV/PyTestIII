import re
import pandas as pd


if '.' in __name__:
    from .utils import frmt, stdSqlData
else:
    from utils import frmt, stdSqlData

from vUtil.vTime import getNow
from vUtil.vTqdm import tqdm, trange

delSizeBulk = 1000

def deleteIndexRows (db, es, table, idCol, tLast=None, tNow=None, where=None, index=None):
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

    where = [
        'ifnull(is_deleted,0)',
        (f'{stdSqlData(tLast)} <= ifnull (updated_at, created_at)' if tLast else ''),
        (f'ifnull (updated_at, created_at) < {stdSqlData(tNow)}' if tNow else ''),
        (f'({where})' if where else ''),
    ]
    where = '\n\tand '.join([x for x in where if x])

    nDel = db.count(table, where=where).values.item()
    db.close()

    tot = {x : 0 for x in index}
    tr = trange(0, nDel, delSizeBulk)
    frmt(f'移除新增删除', tqdm=tr)
    for i in tr:
        frmt(f'移除新增删除{i}/{nDel}', tqdm=tr)
        ids = db.select(idCol, table, i, i + delSizeBulk, where=where)[idCol]
        db.close()

        ids = [str(ids) for x in ids]
        for x in index:
            tot[x] += es.delete_by_query(index=x, body = {
                "query": {
                    "terms": {"_id": ids}
                }
            }).get('deleted', 0)
    return tot
