'''

工具包

----------------------------

setTimeManager : 设置使用的时间管理员
ourError : 文件输出error
ourLog : 文件输出log
frmt : 命令行带时间输出

'''

import os

from vUtil.vTime import getNow, getToday
from vUtil.vFile import fprint
from vUtil.vLog import frmt, VError, VLog
from vGlobals import vGlobals

__path__  = os.path.dirname(os.path.abspath(__file__))

vGlobals.timeManagerType = ''
vGlobals.ourError = VError(path=os.path.join(__path__, f'error{vGlobals.timeManagerType}'))
vGlobals.ourLog = VLog(path=os.path.join(__path__, f'log{vGlobals.timeManagerType}'))

def setTimeManager (tm):
    vGlobals.timeManagerType = tm
    vGlobals.ourError = VError(path=os.path.join(__path__, f'error{vGlobals.timeManagerType}'))
    vGlobals.ourLog = VLog(path=os.path.join(__path__, f'log{vGlobals.timeManagerType}'))

def ourError (error, errorType = ''):
    path = os.path.join(__path__, f'error{vGlobals.timeManagerType}')
    fprint(f'[ERROR] ({getNow()}) {errorType} : {repr(error)}', file=f'error{getToday()}.txt', path=path)

def ourLog (log, logType = ''):
    path = os.path.join(__path__, f'log{vGlobals.timeManagerType}')
    fprint(f'[LOG] ({getNow()}) {logType} : {repr(log)}', file=f'log{getToday()}.txt', path=path)
