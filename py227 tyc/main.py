
import os
from time import sleep, time

if '.' in __name__:
    from .tycSearcher import main as tycSearch
    from .tycSearcher.keywords import keywords
    from .tyc2landinn import main as tyc2landinn
    from .utils import ourError, ourLog, frmt
    from .cfg import updateGap
else:
    from tycSearcher import main as tycSearch
    from tycSearcher.keywords import keywords
    from tyc2landinn import main as tyc2landinn
    from utils import ourError, ourLog, frmt
    from cfg import updateGap

__version__ = 20210615
__author__ = 'LymphV@163.com'

from vUtil.vTqdm import tqdm, trange
from vUtil.vTime import getNow
from vUtil.vEmail import sendEmail

__path__  = os.path.dirname(os.path.abspath(__file__))


def main():
    try:
        iRound = 0
        while 1:
            ### 通过更改文件的时间表示程序仍在运行
            with open(os.path.join(__path__, 'I am running'), 'w'): pass
            
            
            tStart = time()
            
            nKeywords = len(keywords)
            if nKeywords:
                iRound = 0
                ourLog('天眼查接口检索')
                frmt('天眼查接口检索')
                tycSearch()
                
                ourLog('融入landinn')
                frmt('融入landinn')
                tyc2landinn()

                ourLog()

            tEnd = time()
            if tEnd < tStart + updateGap:
                iRound += 1
                with trange(int(tStart + updateGap - tEnd), leave=False) as tr:
                    for i in tr:
                        frmt(f'等待下轮{iRound}', tqdm=tr)
                        sleep(1)
    except Exception as e:
        ourError('service error', str(e))
        sendEmail(str(e), '天眼查更新数据服务中断')
        raise e
        


if __name__ == '__main__':
    main()