'''

工具包

----------------------------

rmUnseen : 去除不可见字符
none2dict : None变为空dict
none2list : None变为空list
ourError : 文件输出error
ourLog : 文件输出log
frmt : 命令行带时间输出
'''

import re
import os

from vUtil.vTime import getNow, getToday
from vUtil.vFile import fprint

__path__  = os.path.dirname(os.path.abspath(__file__))


def rmUnseen (s, none=None):
    '''
    去除不可见字符
    '''
    if s is None: return none
    return re.sub(r'\s+', ' ', str(s))



def none2dict (x):
    return {} if x is None else x

def none2list (x):
    return [] if x is None else x

# def ourError (keyword, error, errorType = ''):
#     path = os.path.join(__path__, 'error')
#     fprint(f'[ERROR] ({getNow()}) {repr(keyword)} : {errorType} : {repr(error)}', file=f'error{getToday()}.txt', path=path)

# def ourLog (keyword, log, logType = ''):
#     path = os.path.join(__path__, 'log')
#     fprint(f'[LOG] ({getNow()}) {repr(keyword)} : {logType} : {repr(log)}', file=f'log{getToday()}.txt', path=path)


from vUtil.vLog import vLog as ourLog, vError as ourError, frmt
