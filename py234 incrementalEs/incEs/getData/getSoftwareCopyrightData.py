
import pandas as pd

from .baseGetData import BaseGetData, rmUnseen, groupConcat


def getActions (data, publish, index):
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


class GetData(BaseGetData):
    '''
    获取软著数据

    ------------

    self.__call__ : 获取范围数据
    '''
    def __init__(self, this, thisEn, table, idCol):
        BaseGetData.__init__(self, this, thisEn, table, idCol)

        self.sTmp = f'''
        create temporary table tmp_{thisEn}
        (
            select  {idCol} as gid,
                    full_name as name,
                    simple_name as simpleName,
                    registration_time,
                    publish_time,
                    event_time
            from {table} as a
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

        self.sSelectPublish = f'''
        select gid, cast(affiliation_id as char) as enterprise_id
        from tmp_{thisEn} as a
        left join softwareCopyright_affiliation as b
        on a.gid = b.sc_id
        and not b.is_deleted;
        '''

        self.sSelectData = f'''
        select gid, name, simpleName, registration_time, publish_time, event_time
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
        publish = db.sql(self.sSelectPublish, ifCommit=1, ifRetry=0)
        db.sql(self.sRmTmp, ifCommit=1, ifRetry=0)
        db.close()
        return data, groupConcat(publish, 'gid', ';')
