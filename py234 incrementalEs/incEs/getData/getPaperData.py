
import pandas as pd

from datetime import datetime, timedelta, timezone
tz = timezone(timedelta(hours=8))

from .baseGetData import BaseGetData, rmUnseen, groupConcat

def getActions (data, publish, index):
    actions = []

    p2s = {publish['gid'][i] : publish['scholar_id'][i] for i in range(len(publish))}

    for i in range(len(data)):
        if data['gid'][i] not in p2s: continue

        ### paper_date
        year = data['paper_year'][i]
        if year is None and not pd.isna(data['paper_date'][i]):
            year = str(data['paper_date'][i].year)

        if year is not None and datetime.now(tz).year < int(year):
            year = None

        action={'_op_type':'index',#操作 index update create delete
            '_index':index,#index
            '_id' : data['gid'][i],
            '_source':
           {
                "id" : data['gid'][i],
                "title" : rmUnseen(data['title'][i]),
                "abstract" : rmUnseen(data['abstract'][i]),
                "keywords" : rmUnseen(data['keywords'][i]),
                "scholars" : p2s[data['gid'][i]],
                "year" : year
            }}
        actions.append(action)
    return actions

class GetData(BaseGetData):
    '''
    获取论文数据
    
    ------------
    
    self.__call__ : 获取范围数据
    '''
    def __init__ (self, this, thisEn, table, idCol):
        BaseGetData.__init__(self, this, thisEn, table, idCol)

        self.sTmp = f'''
        create temporary table tmp_{thisEn}
        (
            select  {idCol} as gid,
                    ifnull(paper_title, paper_title_en) as title,
                    ifnull(keyword, keyword_en) as keywords,
                    cast(paper_year as char) as paper_year,
                    paper_date
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

        self.sSelectPublish = f'''
        select gid, cast(author_id as char) as scholar_id
        from tmp_{thisEn} as a
        left join paper_author_affiliations as b
        on a.gid = b.paper_id 
        and not b.is_deleted;
        '''

        self.sSelectData = f'''
        select gid, title, keywords, paper_year, paper_date, ifnull(abstract, abstract_en) as abstract
        from tmp_{thisEn} as a
        left join papers_abstracts as b 
        on a.gid = b.paper_id
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
        publish = db.sql(self.sSelectPublish, ifCommit=1, ifRetry=0)
        db.sql(self.sRmTmp, ifCommit=1, ifRetry=0)
        db.close()
        return data, groupConcat(publish, 'gid', ';')
