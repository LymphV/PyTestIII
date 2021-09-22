
import pandas as pd

from .baseGetData import MainGetData, addPublishId

__version__ = 20210820
__author__ = 'LymphV@163.com'

def getActions (data, info, index):
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
                "establishmentTime" : info[id]['establishmentTime'],
                "entityType" : info[id]['entityType'],
                "baseInfo" : info[id]['baseInfo'],
                "has_phone" : info[id]['has_phone'],
                "has_email" : info[id]['has_email'],
                "has_weibo" : info[id]['has_weibo'],
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
                "enterprise_id" : str(id),
                "is_chinese" : info[id]['is_chinese'],
                "has_officialPage" : info[id]['has_officialPage'],
                "name" : info[id]['name'],
                "industry" : info[id]['industry'],
                "businessScope" : info[id]['businessScope'],
                "province" : info[id]['province'],
                "city" : info[id]['city'],
                "regCapital" : info[id]['regCapital'],
                "establishmentTime" : info[id]['establishmentTime'],
                "entityType" : info[id]['entityType'],
                "baseInfo" : info[id]['baseInfo'],
                "has_phone" : info[id]['has_phone'],
                "has_email" : info[id]['has_email'],
                "has_weibo" : info[id]['has_weibo'],
            }
        }
        actions.append(action)
    return actions


class GetData(MainGetData):
    '''
    获取企业数据
    
    ------------
    
    self.getRangeData : 获取范围数据
    self.getIdData : 获取指定id数据
    '''
    def __init__ (self, this, thisEn, table, idCol, nIdSep):
        MainGetData.__init__(self, this, thisEn, table, idCol)

        self.sTmpPublish = f'''
        create temporary table tmp_publish
        (
            select affiliation_id as {thisEn}_id, sc_id as publish_id
            from softwareCopyright_affiliation as a
            join tmp_{thisEn} as b
            on a.affiliation_id = b.{thisEn}_id
            and not a.is_deleted
        );'''

        self.sInsertPublish = [f'''
            insert into tmp_publish
            (
                select applicant_id as {thisEn}_id, patent_id as publish_id
                from patent_applicants as a
                join tmp_{thisEn} as b
                on a.applicant_id = b.{thisEn}_id
                and not a.is_deleted
            );
            ''',
            f'''
            insert into tmp_publish
            (
                select affiliation_id as {thisEn}_id, golaxy_product_id as publish_id
                from product as a
                join tmp_{thisEn} as b
                on a.affiliation_id = b.{thisEn}_id
                and not a.is_deleted
            );
            '''
        ]

        def getSqlSelectData (n):
            return f'''
            select  {thisEn}_id,
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
                select  {thisEn}_id, publish_id, softwareCopyright_name, simpleName, patent_title,
                        ifnull(patent_signory, patent_signory_en) as signory,
                        ifnull(patent_abstract, patent_abstract_en) as summary
                from
                (
                    select {thisEn}_id, publish_id, softwareCopyright_name, simpleName, ifnull(patent_title, patent_title_en) as patent_title
                    from
                    (
                        select {thisEn}_id, publish_id, full_name as softwareCopyright_name, simple_name as simpleName
                        from tmp_publish as a
                        left join software_copyright as b 
                        on a.publish_id = b.golaxy_sc_id and not b.is_deleted
                    ) as c
                    left join patent 
                    on c.publish_id = patent.golaxy_patent_id and not patent.is_deleted
                )as d
                left join patent_abstracts 
                on d.publish_id = patent_abstracts.patent_id and not patent_abstracts.is_deleted
            ) as e
            left join product 
            on e.publish_id = product.golaxy_product_id and not product.is_deleted;
            '''

        self.sSelectData = getSqlSelectData(nIdSep)
        self.sSelectDataMini = getSqlSelectData(None)

        self.sSelectInfo = f'''
        select  affiliation_id as {thisEn}_id,
                cast(not is_abroad as char) as is_chinese,
                official_page is not null as has_officialPage,
                ifnull(display_name, display_name_en) as name,
                industry,
                business_scope as businessScope,
                reg_province as province,
                reg_city as city,
                cast(reg_capital_standard as char) as regCapital,
                establishment_time as establishmentTime,
                cast(entity_type as char) as entityType,
                base_info as baseInfo,
                (phone_number is not null or ifnull(phone_list, '') not in ('', '[]')) as has_phone,
                (email is not null or ifnull(email_list, '') not in('', '[]')) as has_email,
                weibo is not null as has_weibo
        from tmp_{thisEn} as a
        join {table} as b
        on a.{thisEn}_id = b.{idCol} and not b.is_deleted and not b.is_new;
        '''

    def stdData (self, data):
        return {
            data[f'{self.thisEn}_id'][i] : {
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

    def stdInfo (self, info):
        return {
            info[f'{self.thisEn}_id'][i] : {
                'is_chinese' : info['is_chinese'][i],
                'has_officialPage' : info['has_officialPage'][i],
                'name' : info['name'][i],
                'industry' : info['industry'][i],
                'businessScope' : info['businessScope'][i],
                'province' : info['province'][i],
                'city' : info['city'][i],
                'regCapital' : info['regCapital'][i],
                'establishmentTime' : (None if info['establishmentTime'][i] is pd.NaT
                                        else info['establishmentTime'][i]),
                'entityType' : info['entityType'][i],
                'baseInfo' : info['baseInfo'][i],
                'has_phone' : info['has_phone'][i],
                'has_email' : info['has_email'][i],
                'has_weibo' : info['has_weibo'][i],
            } for i in range(len(info))
        }
