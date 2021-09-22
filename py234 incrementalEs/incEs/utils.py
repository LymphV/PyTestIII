'''

工具包

----------------------------

none2dict : None变为空dict
none2list : None变为空list
setTimeManager : 设置时间管理员
getTimeManager : 获取时间管理员
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


from vMysql import stdSqlData
from vUtil.vLog import frmt
from vGlobals import vGlobals

__path__  = os.path.dirname(os.path.abspath(__file__))



def none2dict (x):
    return {} if x is None else x

def none2list (x):
    return [] if x is None else x

def getTimeManager ():
    return vGlobals.timeManagerType

def ourError (error, errorType = ''):
    path = os.path.join(__path__, f'error{vGlobals.timeManagerType}')
    fprint(f'[ERROR] ({getNow()}) {errorType} : {repr(error)}\n', file=f'error{getToday()}.txt', path=path)

def ourLog (log, logType = ''):
    path = os.path.join(__path__, f'log{vGlobals.timeManagerType}')
    fprint(f'[LOG] ({getNow()}) {logType} : {repr(log)}\n', file=f'log{getToday()}.txt', path=path)
