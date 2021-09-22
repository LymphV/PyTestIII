
import pandas as pd

from .baseGetData import BaseGetData, rmUnseen, groupConcat

def getActions (data, publish, index):
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

class GetData(BaseGetData):
    '''
    获取专利数据
    
    ------------
    
    self.__call__ : 获取范围数据
    '''
    def __init__ (self, this, thisEn, table, idCol):
        BaseGetData.__init__(self, this, thisEn, table, idCol)

        self.sTmp = f'''
        create temporary table tmp_{thisEn}
        (
            select  {idCol} as gid,
                    ifnull(patent_title, patent_title_en) as title,
                    applicant_date,
                    grant_date,
                    publication_date
            from {table} as a
            join
            (
                select id from %s
                where id > %d order by id
                limit %d
            ) as b
            on a.{idCol} = b.id and not a.is_deleted
        );
        '''

        self.sSelectPublishScholar = f'''
        select gid, cast(author_id as char) as scholar_id, null as enterprise_id
        from tmp_{thisEn} as a
        left join patent_authors as b
        on a.gid = b.patent_id 
        and not b.is_deleted;
        '''

        self.sSelectPublishEnterprise = f'''
        select gid, null as scholar_id, cast(applicant_id as char) as enterprise_id
        from tmp_{thisEn} as c
        left join patent_applicants as d
        on c.gid = d.patent_id
        and not d.is_deleted;
        '''

        self.sSelectData = f'''
        select  gid, title, applicant_date, grant_date, publication_date,
                ifnull(patent_signory, patent_signory_en) as signory,
                ifnull(patent_abstract, patent_abstract_en) as summary
        from tmp_{thisEn} as a
        left join patent_abstracts as b 
        on a.gid = b.patent_id
        and not b.is_deleted;
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
        ps = db.sql(self.sSelectPublishScholar, ifCommit=1, ifRetry=0)
        pe = db.sql(self.sSelectPublishEnterprise, ifCommit=1, ifRetry=0)
        db.sql(self.sRmTmp, ifCommit=1, ifRetry=0)
        db.close()

        publish = ps.append(pe, ignore_index=True)
        return data, groupConcat(publish, 'gid', ';')
