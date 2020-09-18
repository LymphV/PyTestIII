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

__version__ = 20200917

outputFile = 'output.txt'



@click.command()
@click.option('-k', prompt='key word', help='key word')
@click.option('-n', default=None, help='number of papers', type=int)
@click.option('-s', default='', help='custom sorting')
@click.option('--sy', default=None, help='start year',type=int)
@click.option('--ey', default=None, help='end year',type=int)
@click.option('-o', default=outputFile, help='output file')
def main (k, n, s, sy, ey, o):
    timeSpan = None if sy is None and ey is None else (sy, ey)
    
    keyWord = k
    nReq = n
    sortReq = s
    outFile = o
    
    wospidey = Wospidey()
    
    with open(outFile, 'w') as f:
        f.write('[\n')
        
        '''for record in wospidey.crawl(keyWord, nReq, sortReq, timeSpan):
            f.write ('"invalid paper"' if not record else str(record.__dict__))
            f.write (',\n')
        f.write('\n]\n')'''
                
        try:
            for record in wospidey.crawl(keyWord, nReq, sortReq, timeSpan):
                f.write ('"invalid paper"' if not record else str(record.__dict__))
                f.write (',\n')
        except Exception as e:
            print ('ERROR : "%s"' % e)
        finally:
            f.write('\n]\n')
    
    wospidey.close()





if __name__ == '__main__':
    main ()