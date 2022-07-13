'''

工具包

----------------------------

rmUnseen : 去除不可见字符
groupConcat : 组合并
none2dict : None变为空dict
none2list : None变为空list
ourError : 文件输出error
ourLog : 文件输出log
frmt : 命令行带时间输出

stdSqlData : 变量插入sql语句格式化
'''

import re
import os
import pandas as pd

from vUtil.vTime import getNow, getToday
from vUtil.vFile import fprint
from datetime import datetime, timedelta, timezone


if '.' in __name__:
    from .tmpIncTable.utils import stdSqlData
else:
    from tmpIncTable.utils import stdSqlData

__path__  = os.path.dirname(os.path.abspath(__file__))


def rmUnseen (s, none = ''):
    '''
    去除不可见字符
    '''
    if s is None: return none
    return re.sub(r'\s+', ' ', str(s))

def groupConcat (data, field = 'scholar_id', sep = '\n'):
    return pd.DataFrame([
        [x] +
        [
            sep.join([rmUnseen(data[j][i]) for i in range(len(data)) if data[field][i] == x and data[j][i]])
            for j in data if j != field
        ] for x in sorted(set(data[field]))
    ], columns = [*data])


def none2dict (x):
    return {} if x is None else x

def none2list (x):
    return [] if x is None else x

def ourError (error, errorType = ''):
    path = os.path.join(__path__, 'error')
    fprint(f'[ERROR] ({getNow()}) {errorType} : {repr(error)}\n', file=f'error{getToday()}.txt', path=path)

def ourLog (keyword, log, logType = ''):
    path = os.path.join(__path__, 'log')
    fprint(f'[LOG] ({getNow()}) {logType} : {repr(log)}\n', file=f'log{getToday()}.txt', path=path)

def frmt (*s, start='', tqdm=None, **k):
    if tqdm is None:
        print (f'{start}({getNow()})', *s, **k)
    else:
        s = [f'{start}({getNow()})', *[str(x) for x in s]]
        tqdm.set_description(' '.join(s))
