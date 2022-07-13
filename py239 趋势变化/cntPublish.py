import pandas as pd
from tqdm import trange

def cntPublish (es, *keywords, start=1900, end=2022, ifPaper=True, ifPatent=True):
    '''
    计数关键词的相关成果数
    
    Parameters
    ----------
    es : es连接对象，elasticsearch包Elasticsearch类对象
    *keywords : 变长参数，检索的关键词列表
    start : 检索起始年份，左闭区间，默认值1900
    end : 检索终止年份，右开区间，默认值2022
    ifPaper : 是否计数论文，默认值True
    ifPatent : 是否计数专利，默认值True
    
    Returns
    -------
    pd.DataFrame : 最多四列，year年份、paper论文数（如果ifPaper=True）、patents专利数（如果ifPatent=True）、total总数
    
    '''
    bodyPaper = lambda year : ({
        "track_total_hits": True, 
        "query": {
            "bool": {
                "must": [
                    {"term": {"year": year}},
                    {
                        "bool": {
                            "should": sum([
                                [
                                    {"match_phrase": {"title": {"query": k,"slop": 10}}},
                                    {"match_phrase": {"abstract": {"query": k,"slop": 10}}},
                                    {"match_phrase": {"keywords": {"query": k,"slop": 10}}}
                                ] for k in keywords
                            ], [])
                        }
                    }
                ]
            }
        },
        "size": 3
    }, 'landinn_paper')
    
    bodyPatent = lambda year : ({
        "track_total_hits": True,
        "query": {
            "bool": {
                "must": [
                    {"range": {"applicant_date": {"gte": f"{year}-01-01 00:00:00", "lt": f"{year+1}-01-01 00:00:00", "format": "yyyy-MM-dd HH:mm:ss"}}},
                    {
                        "bool": {
                            "should": sum([
                                [
                                    {"match_phrase": {"title": {"query": k,"slop": 10}}},
                                    {"match_phrase": {"summary": {"query": k,"slop": 10}}},
                                    {"match_phrase": {"signory": {"query": k,"slop": 10}}},
                                ] for k in keywords
                            ], [])
                        }
                    }
                ]
            }
        },
        "size": 3
    }, 'landinn_patent')
    
    publishes = {}
    if ifPaper: publishes['paper'] = bodyPaper
    if ifPatent: publishes['patent'] = bodyPatent
    
    cols = ['year' + 'total']
    rst = pd.DataFrame(columns=['year', *publishes, 'total'])

    for year in trange(start, end):
        row = [es.search(*body(year))['hits']['total']['value'] for col, body in publishes.items()]
        rst.loc[len(rst)] = [year, *row, sum(row)]
    return rst
    