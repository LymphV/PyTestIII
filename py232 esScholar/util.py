from vUtil.vTime import getNow
import re
import pandas as pd

from vUtil.vTqdm import tqdm, trange

from vUtil.vLog import frmt


def rmUnseen (s, none=''):
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


delSizeBulk = 1000

def deleteIndexRows (db, es, table, idCol, hasIsNew=False, where=None, index=None):
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
        (f'({where})' if where else ''),
    ]
    
    where = '\n\tand '.join([x for x in where if x])
    
    nDel = db.count(table, where=where).values.item()
    db.close()
    
    tot = {x : 0 for x in index}
    with trange(0, nDel, delSizeBulk) as tr:
        for i in tr:
            frmt(f'{i}/{nDel}', tqdm=tr)
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