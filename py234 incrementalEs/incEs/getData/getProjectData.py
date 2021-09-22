
import pandas as pd

from .baseGetData import BaseGetData, rmUnseen, groupConcat

def getActions (data, publish, index):
    actions = []

    p2s = {publish['gid'][i] : publish['scholar_id'][i] for i in range(len(publish))}

    for i in range(len(data)):
        if data['gid'][i] not in p2s: continue
        action={'_op_type':'index',#操作 index update create delete
            '_index':index,#index
            '_id' : data['gid'][i],
            '_source':
           {
                "id" : data['gid'][i],
                "title" : rmUnseen(data['title'][i]),
                "discipline" : rmUnseen(data['discipline'][i]),
                "description" : rmUnseen(data['description'][i]),
                "scholars" : p2s[data['gid'][i]],
                "start_year" : data['start_year'][i],
                "end_year" : data['end_year'][i]
            }
        }
        actions.append(action)
    return actions


class GetData(BaseGetData):
    '''
    获取项目数据

    ------------

    self.__call__ : 获取范围数据
    '''

    def __init__ (self, this, thisEn, table, idCol):
        BaseGetData.__init__(self, this, thisEn, table, idCol)

        self.sTmp = f'''
        create temporary table tmp_{thisEn}
        (
            select {idCol} as gid,
                ifnull(project_title, project_title_en) as title,
                ifnull(discipline_first, discipline_first_en) as d1,
                ifnull(discipline_secondary, discipline_secondary_en) as d2,
                ifnull(discipline_tertiary, discipline_tertiary_en) as d3,
                cast(start_year as char) as start_year,
                cast(end_year as char) as end_year
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
        select gid, cast(author_id as char) as scholar_id
        from tmp_{thisEn} as a
        left join project_authors as b
        on a.gid = b.project_id
        and not b.is_deleted;
        '''

        self.sSelectData = '''
        select  gid, title,
                if (d1 is null and d2 is null and d3 is null, null,
                    concat('{', ifnull(d1, ''), '}{', ifnull(d2, ''), '}{', ifnull(d3, ''),'}')
                ) as discipline,
                ifnull(project_description, project_description_en) as description,
                start_year, end_year
        from tmp_%s as a
        left join project_abstracts as b
        on a.gid = b.project_id
        and not b.is_deleted;
        ''' % thisEn

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
