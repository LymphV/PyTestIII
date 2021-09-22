
import pandas as pd
from .baseGetData import MainGetData, addPublishId


def getActions (data, info, index):
    actions = []
    for id in info:
        action={'_op_type':'index',###操作 index update create delete
            '_index': index,#index
            '_id' : str(id),
            '_source':
           {
                "scholar_id" : str(id),
                "paper_title" : data.get(id, {}).get('paper_title', ''),
                "paper_abstract" : data.get(id, {}).get('abstract', ''),
                "paper_keywords" : data.get(id, {}).get('keywords', ''),
                "patent_title" : data.get(id, {}).get('patent_title', ''),
                "patent_signory" : data.get(id, {}).get('signory', ''),
                "patent_summary" : data.get(id, {}).get('summary', ''),
                "project_title" : data.get(id, {}).get('project_title', ''),
                "project_discipline" : data.get(id, {}).get('discipline', ''),
                "project_description" : data.get(id, {}).get('description', ''),
                "is_chinese" : info[id]['is_chinese'],
                "has_email" : info[id]['has_email'],
                "has_phone" : info[id]['has_phone'],
                "birthday" : info[id]['birthday'],
                "title" : info[id]['title'],
                "name" : info[id]['name'],
                "brief" : info[id]['brief'],
                "major" : info[id]['major'],
            }
        }
        actions.append(action)
    return actions

def getHighLightActions (data, info, indexHl):
    actions = []
    for id in info:
        action={'_op_type':'index',###操作 index update create delete
            '_index': indexHl,#index
            '_id' : str(id),
            '_source':
           {
                "scholar_id" : str(id),
                "is_chinese" : info[id]['is_chinese'],
                "has_email" : info[id]['has_email'],
                "has_phone" : info[id]['has_phone'],
                "birthday" : info[id]['birthday'],
                "title" : info[id]['title'],
                "name" : info[id]['name'],
                "brief" : info[id]['brief'],
                "major" : info[id]['major'],
            }
        }
        actions.append(action)
    return actions

class GetData(MainGetData):
    '''
    获取学者数据

    ------------

    self.getRangeData : 获取范围数据
    self.getIdData : 获取指定id数据
    '''
    def __init__ (self, this, thisEn, table, idCol, nIdSep):
        MainGetData.__init__(self, this, thisEn, table, idCol)

        self.sTmpPublish = f'''
        create temporary table tmp_publish
        (
            select author_id as {thisEn}_id, paper_id as publish_id
            from paper_author_affiliations as a
            join tmp_{thisEn} as b
            on a.author_id = b.{thisEn}_id
            and not a.is_deleted
        );'''

        self.sInsertPublish = [f'''
            insert into tmp_publish
            (
                select author_id as {thisEn}_id, patent_id as publish_id
                from patent_authors as a
                join tmp_{thisEn} as b
                on a.author_id = b.{thisEn}_id
                and not a.is_deleted
            );
            ''',
            f'''
            insert into tmp_publish
            (
                select author_id as {thisEn}_id, project_id as publish_id
                from project_authors as a
                join tmp_{thisEn} as b
                on a.author_id = b.{thisEn}_id
                and not a.is_deleted
            );
            '''
        ]

        def getSqlSelectData (n):
            return f'''
            select  {thisEn}_id,
                    {addPublishId("paper_title", n)} as paper_title,
                    {addPublishId("keywords", n)} as keywords,
                    {addPublishId("abstract", n)} as abstract,
                    {addPublishId("patent_title", n)} as patent_title,
                    {addPublishId("signory", n)} as signory,
                    {addPublishId("summary", n)} as summary,
                    {addPublishId("project_title", n)} as project_title,
                    {addPublishId("if (d1 is null and d2 is null and d3 is null,null,concat('{',ifnull(d1,''),'}{',ifnull(d2,''),'}{',ifnull(d3,''),'}'))",n)} as discipline,
                    {addPublishId("ifnull(project_description, project_description_en)", n)} as project_description
            from
            (
                select  {thisEn}_id, publish_id, paper_title, keywords, abstract, patent_title, signory, summary,
                        ifnull(project_title, project_title_en) as project_title,
                        ifnull(discipline_first, discipline_first_en) as d1,
                        ifnull(discipline_secondary, discipline_secondary_en) as d2,
                        ifnull(discipline_tertiary, discipline_tertiary_en) as d3
                from
                (
                    select  {thisEn}_id, publish_id, paper_title, keywords, abstract, patent_title,
                            ifnull(patent_signory, patent_signory_en) as signory,
                            ifnull(patent_abstract, patent_abstract_en) as summary
                    from
                    (
                        select {thisEn}_id, publish_id, paper_title, keywords, abstract, ifnull(patent_title, patent_title_en) as patent_title
                        from
                        (
                            select {thisEn}_id, publish_id, paper_title, keywords, ifnull(abstract, abstract_en) as abstract
                            from
                            (
                                select {thisEn}_id, publish_id, ifnull(paper_title, paper_title_en) as paper_title, ifnull(keyword, keyword_en) as keywords
                                from tmp_publish as a
                                left join papers 
                                on a.publish_id = papers.golaxy_paper_id and not papers.is_deleted
                            ) as b
                            left join papers_abstracts 
                            on b.publish_id = papers_abstracts.paper_id and not papers_abstracts.is_deleted
                        ) as c
                        left join patent 
                        on c.publish_id = patent.golaxy_patent_id and not patent.is_deleted
                    )as d
                    left join patent_abstracts 
                    on d.publish_id = patent_abstracts.patent_id and not patent_abstracts.is_deleted
                ) as e
                left join project 
                on e.publish_id = project.golaxy_project_id and not project.is_deleted
            )as f
            left join project_abstracts 
            on f.publish_id = project_abstracts.project_id and not project_abstracts.is_deleted;
            '''

        self.sSelectData = getSqlSelectData(nIdSep)
        self.sSelectDataMini = getSqlSelectData(None)

        self.sSelectInfo = f'''
        select  {thisEn}_id,
                {1 if len(this) == 2 else "not is_abroad" } as is_chinese,
                if(phone is null, 0, 1) as has_phone,
                if(email is null, 0, 1) as has_email,
                ifnull(title, title_en) as title,
                birthday,
                display_name as name,
                brief,
                ifnull(major, major_en) as major
        from tmp_{thisEn} as a
        join {table} as b
        on a.{thisEn}_id = b.{idCol} and not b.is_deleted and not b.is_new
        {"where not ifnull(is_abroad, 0)" if len(this) == 2 else "" };
        '''

    def stdData (self, data):
        return {
            data[f'{self.thisEn}_id'][i] : {
                "paper_title" : data['paper_title'][i],
                "abstract" : data['abstract'][i],
                "keywords" : data['keywords'][i],
                "patent_title" : data['patent_title'][i],
                "signory" : data['signory'][i],
                "summary" : data['summary'][i],
                "project_title" : data['project_title'][i],
                "discipline" : data['discipline'][i],
                "project_description" : data['project_description'][i],
            } for i in range(len(data))
        }

    def stdInfo (self, info):
        return {
            info[f'{self.thisEn}_id'][i] : {
                'is_chinese' : info['is_chinese'][i],
                'has_email' : info['has_email'][i],
                'has_phone' : info['has_phone'][i],
                'birthday' : None if info['birthday'][i] is pd.NaT else info['birthday'][i],
                'title' : info['title'][i],
                'name' : info['name'][i],
                'brief' : info['brief'][i],
                'major' : info['major'][i],
            } for i in range(len(info))
        }
