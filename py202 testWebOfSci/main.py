'''

wospidey
========
提供：
    1.以wos核心合集为数据库，按指定时间跨度的关键词检索
    2.以日期降序、被引频次降序、相关性等排序方式排序检索结果
    3.从检索结果中抽取文章的标题、作者、通讯作者、电子邮箱等字段
    
'''

import click
import pandas as pd
import os

if __name__ == '__main__':
    from wospidey import Wospidey
    from sortId import dft as sortDft, str2SortId
    from searchFieldIndex import dft as fieldDft, str2SearchFieldIndex
else:
    from .wospidey import Wospidey
    from .sortId import dft as sortDft, str2SortId
    from .searchFieldIndex import dft as fieldDft, str2SearchFieldIndex

__version__ = 20200921


folder = 'output'
if folder not in os.listdir(): os.mkdir(folder)
dftOutputFile = folder + '/%s(%s,%s,%s%s).csv'


helpNReq = 'number of papers, default is all'
helpSortReq = 'custom sorting'
helpFieldReq = 'custom search field'
helpStartYear = 'start year, default is the earliest year wos have'
helpEndYear = 'end year, default is the latest year wos have'
helpOutputFile = 'output file, default is {keyWord(nReq,sortReq,fieldReq[,(startYear,endYear)])}.csv'

###排序代码选项
typeSortReq = click.Choice(str2SortId, case_sensitive=False)

###search field代码选项
typeFieldReq = click.Choice([
                    x for x in str2SearchFieldIndex if x not in['LA','DT']
                ], case_sensitive=False)

"""
def __addRecord (mp, rcd):
    '''
    添加一条记录，用于去重
    本用于email去重
    '''
    emails, cauthors = rcd.emails, rcd.cauthors
    
    if emails not in mp:
        mp[emails] = cauthors
        return
    if len(cauthors) > len(mp[emails]):
        mp[emails] = cauthors
"""

def __saveRecords (records, outputFile):
    '''
    保存记录到csv
    无效记录不存
    '''
    #mp = {}
    rcds = []
    for rcd in records:
        if not rcd: continue
        
        title, authors, emails, cauthors = (
            rcd.title, 
            rcd.authors.replace('; ',';').replace(';',';\n'), 
            rcd.emails.replace(';',';\n'), 
            rcd.cauthors.replace('; ',';').replace(';',';\n')
        )
        rcds += [(title, authors, emails, cauthors)]
        
        ###多通讯作者的人名与邮箱匹配问题
        ##  最初设想是按先后顺序匹配，但已找到反例，链接、题目如下
        ##  http://apps.webofknowledge.com/full_record.do?product=WOS&search_mode=GeneralSearch&qid=5&SID=7FjRmPV5c9CIWq9EqPo&page=1&doc=6
        ##  Superior catalytic effect of facile synthesized LaNi4.5Mn0.5 submicroparticles on the hydrogen storage properties of MgH2
        ##  还有将作者的email都列出来的，链接、题目如下
        ##  http://apps.webofknowledge.com/full_record.do?product=WOS&search_mode=GeneralSearch&qid=5&SID=7FjRmPV5c9CIWq9EqPo&page=1&doc=21
        ##  Distributed Control of Active Cell Balancing and Low-Voltage Bus Regulation in Electric Vehicles Using Hierarchical Model-Predictive Control
        ##  如果真要做，打算使用编辑距离最小或最长匹配最大做匹配，大概高级人工智能·沈华伟·博弈II中讲的宿舍分配问题最优匹配的市场结清价格可能解决
        ##  很大的问题，目前没有需求
        '''
        if ';' in emails and ';' in cauthors:
            listEmail = emails.split(';')
            listCauthor = cauthors.split(';')
            if len(listEmail) == len(listCauthor):
                
                continue'''
        #__addRecord (mp, rcd)

    titles, authorss, emailss, cauthorss = [*zip(*rcds)]
    #emailss, cauthorss = [*zip(*mp.items())]
    pd.DataFrame.from_dict({
        'title' : titles,
        'authors' : authorss,
        'emails' : emailss,
        'corresponding authors' : cauthorss,
    }).to_csv(outputFile, index_label='index')
            



@click.command()
@click.option('-k', 'keyWord', prompt='key word', help='key word to search')
@click.option('-n', 'nReq', default=None, help=helpNReq, type=int, show_default=True)
@click.option('-s', 'sortReq', default=sortDft, help=helpSortReq, type=typeSortReq, show_default=True)
@click.option('-f', 'fieldReq', default=fieldDft, help=helpFieldReq, type=typeFieldReq, show_default=True)
@click.option('--sy', 'startYear', default=None, help=helpStartYear,type=int, show_default=True)
@click.option('--ey', 'endYear', default=None, help=helpEndYear,type=int, show_default=True)
@click.option('-o', 'outputFile', default=None, help=helpOutputFile, show_default=True)
def main (keyWord, nReq, sortReq, fieldReq, startYear, endYear, outputFile):
    #print(f'keyWord${keyWord}$ nReq${nReq}$',
    #        f'sortReq${sortReq}$ startYear${startYear}$',
    #        f'endYear${endYear}$ outputFile${outputFile}$')
    #return
    
    timeSpan = None if startYear is None and endYear is None else (startYear, endYear)
    if outputFile is None or outputFile == '':
        sNReq = 'all' if nReq is None or nReq < 0 else str(nReq)
        sTimeSpan = '' if timeSpan is None else (
            ',(%s,%s)' % ('' if startYear is None else startYear,
                          '' if endYear is None else endYear)
        )
        outputFile = dftOutputFile % (keyWord, sNReq, sortReq, fieldReq, sTimeSpan)
    
    ###outputFile路径错误报错
    try:
        with open(outputFile, 'w') as f: pass
    except FileNotFoundError as e:
        print (f'ERROR : "{e}"')
    
    wospidey = Wospidey()
    records = []
    try:
        for record in wospidey.crawl(keyWord, nReq, sortReq, fieldReq, timeSpan):
            records += [record]
    except Exception as e:
        print (f'ERROR : "{e}"')
    finally:
        __saveRecords(records, outputFile)
        wospidey.close()











if __name__ == '__main__':
    main ()