'''

工具包

----------------------------

ourError : 文件输出error
ourLog : 文件输出log
frmt : 命令行带时间输出
'''
import os
from vUtil.vTime import getNow, getToday
from vUtil.vFile import fprint

__path__  = os.path.dirname(os.path.abspath(__file__))



# def ourError (error, errorType = ''):
#     path = os.path.join(__path__, 'error')
#     fprint(f'[ERROR] ({getNow()}) {errorType} : {repr(error)}\n', file=f'error{getToday()}.txt', path=path)

# def ourLog (log, logType = ''):
#     path = os.path.join(__path__, 'log')
#     fprint(f'[LOG] ({getNow()}) {logType} : {repr(log)}\n', file=f'log{getToday()}.txt', path=path)

from vUtil.vLog import vLog as ourLog, vError as ourError, frmt

#def frmt (*s, start='', tqdm=None, **k):
#    if tqdm is None: 
#        print (f'{start}({getNow()})', *s, **k)
#    else:
#        s = [f'{start}({getNow()})', *[str(x) for x in s]]
#        tqdm.set_description(' '.join(s))
