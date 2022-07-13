'''

获取学者数据

viewScholar : 构建了一个查看全部学者的视图
viewScholarAbroad : 构建了一个查看全部国外学者的视图


获取数据返回值格式
data, info : {学者id : {字段 : 内容}}

data字段 : 
['paper_title',
 'abstract',
 'keywords',
 'patent_title',
 'signory',
 'summary',
 'project_title',
 'discipline',
 'project_description'].

info字段 :
['is_chinese', 'has_email', 'has_phone', 'birthday', 'title', 'name', 'brief']
 

getScholarData : 获取学者数据
    getScholarData.getRangeData
    
        获取范围数据
            
        Parameters
        ----------
        now : 当前偏移量
        sizeBulk : bulk大小
    
        Returns
        -------
        data, info : {学者id : {}}
    getScholarData.getIdData
    
        获取指定id数据
            
        Parameters
        ----------
        id : 指定id
    
    
getScholarAbroadData : 获取国外学者数据
    getScholarAbroadData.getRangeData
    
        获取范围数据
            
        Parameters
        ----------
        now : 当前偏移量
        sizeBulk : bulk大小
    
    getScholarAbroadData.getIdData
    
        获取指定id数据
            
        Parameters
        ----------
        id : 指定id




使用方法（国外学者同理）
--------

from scholars import getScholarData, viewScholar, getScholarAbroadData, viewScholarAbroad

nScholar = len(viewScholar)

step = 10


for i in range(0, nScholar, step):
    data, info = getScholarData.getRangeData(i, step)

'''

__version__ = 20210702
__author__ = 'LymphV@163.com'

from .getData.getScholarData import GetData
from .vMysql import MysqlProxy
from .tmpIncTable.viewAll import ViewAll

db = MysqlProxy()


viewScholar = ViewAll(db, 'scholar', 'authors', 'golaxy_author_id', True)
viewScholarAbroad = ViewAll(db, 'scholar_abroad', 'authors_en', 'golaxy_author_id', True)

viewScholar.start()
viewScholarAbroad.start()


getScholarData = GetData(db, viewScholar.tableTmp, '学者', 'scholar', 'authors', 'golaxy_author_id', 0)
getScholarAbroadData = GetData(db, viewScholarAbroad.tableTmp, '国外学者', 'scholar_abroad', 'authors_en', 'golaxy_author_id', 0)



