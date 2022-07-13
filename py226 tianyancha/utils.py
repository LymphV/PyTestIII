'''

工具包

----------------------------

typeOfScript : 判断脚本运行的环境
rmUnseen : 去除不可见字符
none2dict : None变为空dict
none2list : None变为空list
ourError : 文件输出error
ourLog : 文件输出log
frmt : 命令行带时间输出
'''

import re

from vUtil.vTime import getNow
from vUtil.vFile import fprint

    

def typeOfScript():
    '''
    判断脚本运行的环境
    '''
    try:
        ipy_str = str(type(get_ipython()))
        if 'zmqshell' in ipy_str:
            return 'jupyter'
        if 'terminal' in ipy_str:
            return 'ipython'
    except:
        return 'terminal'
        

def rmUnseen (s):
    '''
    去除不可见字符
    '''
    if s is None: return None
    return re.sub(r'\s+', ' ', str(s))

def none2dict (x):
    return {} if x is None else x

def none2list (x):
    return [] if x is None else x

def ourError (keyword, error, errorType = ''):
    fprint(f'[ERROR] ({getNow()}) {repr(keyword)} : {errorType} : {repr(error)}\n', file='error.txt', path='error')

def ourLog (keyword, log, logType = ''):
    fprint(f'[LOG] ({getNow()}) {repr(keyword)} : {logType} : {repr(log)}\n', file='log.txt', path='log')

def frmt (*s, **k):
    print (f'\r({getNow()})', *s, **k)