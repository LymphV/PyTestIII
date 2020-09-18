'''

wospidey
========
提供：
    1.以wos核心合集为数据库，按指定时间跨度的关键词检索
    2.以日期降序、被引频次降序、相关性等排序方式排序检索结果
    3.从检索结果中抽取文章的标题、作者、通讯作者、电子邮箱等字段
    
'''

import click

from wospidey import Wospidey
from sortId import str2SortId

__version__ = 20200918

dftOutputFile = 'output.txt'


helpNReq = 'number of papers, default is all'
helpStartYear = 'start year, default is the earliest year wos have'
helpEndYear = 'end year, default is the latest year wos have'

###排序代码选项
typeSortReq = click.Choice([*str2SortId], case_sensitive=False)


@click.command()
@click.option('-k', 'keyWord', prompt='key word', help='key word to search')
@click.option('-n', 'nReq', default=None, help=helpNReq, type=int, show_default=True)
@click.option('-s', 'sortReq', default='PYD', help='custom sorting', type=typeSortReq, show_default=True)
@click.option('--sy', 'startYear', default=None, help=helpStartYear,type=int, show_default=True)
@click.option('--ey', 'endYear', default=None, help=helpEndYear,type=int, show_default=True)
@click.option('-o', 'outputFile', default=dftOutputFile, help='output file', show_default=True)
def main (keyWord, nReq, sortReq, startYear, endYear, outputFile):
    #print(f'keyWord${keyWord}$ nReq${nReq}$',
    #        f'sortReq${sortReq}$ startYear${startYear}$',
    #        f'endYear${endYear}$ outputFile${outputFile}$')
    #return
    
    timeSpan = None if startYear is None and endYear is None else (startYear, endYear)
    
    ###outputFile路径错误报错
    try:
        with open(outputFile, 'w') as f:
            wospidey = Wospidey()
            f.write('[\n')
            
            '''for record in wospidey.crawl(keyWord, nReq, sortReq, timeSpan):
                f.write ('"invalid paper"' if not record else str(record.__dict__))
                f.write (',\n')
            f.write('\n]\n')'''
            
            ###paper页打不开报错，搜索失败报错，起止时间报错，等
            try:
                for record in wospidey.crawl(keyWord, nReq, sortReq, timeSpan):
                    f.write ('"invalid paper"' if not record else str(record.__dict__))
                    f.write (',\n')
            except Exception as e:
                print (f'ERROR : "{e}"')
            finally:
                f.write('\n]\n')
    
                wospidey.close()
    except FileNotFoundError as e:
        print (f'ERROR : "{e}"')




if __name__ == '__main__':
    main ()