
import pandas as pd

from .baseGetData import BaseGetData, rmUnseen

def getActions (data, index):
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


class GetData(BaseGetData):
    '''
    获取产品数据
    
    ------------
    
    self.__call__ : 获取范围数据
    '''
    def __init__ (self, this, thisEn, table, idCol):
        BaseGetData.__init__(self, this, thisEn, table, idCol)

        self.sTmp = f'''
        create temporary table tmp_{thisEn}
        (
            select {idCol} as gid, product_name as name, hangye, yewu, setup_time,
                cast(affiliation_id as char) as enterprises
            from
            {table} as a
            join
            (
                select id from %s
                where id > %d order by id
                limit %d
            ) as b
            on a.{idCol} = b.id
            and not a.is_deleted
        );
        '''

        self.sSelectData = f'''
        select  gid, name, hangye, yewu, setup_time, enterprises
        from tmp_{thisEn};
        '''

    def _getData (self, db, tableTmp, now, sizeBulk, lastId=-1):
        '''
        获取范围数据
        
        Parameters
        ----------
        db : MySQLProxy，数据库连接
        tableTmp : 临时表名
        now : 当前偏移量
        sizeBulk : bulk大小
        '''
        
        db.sql(self.sTmp % (tableTmp, lastId, sizeBulk), ifCommit=1, ifRetry=0)

        data = db.sql(self.sSelectData, ifCommit=1, ifRetry=0)
        db.sql(self.sRmTmp, ifCommit=1, ifRetry=0)
        db.close()
        return data,
