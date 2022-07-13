'''
TimeManager

-----------

管理更新时间
TimeManager.last : 上次更新时间
TimeManager.now : 本次更新时间

TimeManager.close : 关闭，保存本次更新时间
'''

import pandas as pd
import os
from vUtil.vTime import getNow, getToday



defFile = 'timeManager.csv'
startTime = '2021-04-22 23:59:00'
col = 'time'

### 默认文件存储条数
nKeep = 1000

__path__  = os.path.dirname(os.path.abspath(__file__))

class TimeManager:
    '''
    TimeManager

    -----------

    管理更新时间
    TimeManager.last : 上次更新时间
    TimeManager.now : 本次更新时间

    TimeManager.close : 关闭，保存本次更新时间
    '''
    
    __version__ = 20210507
    __author__ = 'LymphV@163.com'
    
    def __init__ (this, file=defFile):
        this.data = this.last = this.now = this.log = None
        this.file = os.path.join(__path__, file)
        this.logPath = os.path.join(__path__, 'log')
        this.logFile = os.path.join(this.logPath, f'{getToday()}.csv')
        this.start()
    
    def __repr__ (this):
        return repr({'last' : this.last, 'now' : this.now})
    
    def __str__ (this):
        return repr(this)
    
    def start (this):
        file = this.file
        if not os.path.exists(file):
            this.data = pd.DataFrame({col : [startTime]})
        else:
            this.data = pd.read_csv(file)
        
        if not os.path.exists(this.logPath): os.makedirs(this.logPath)
        if not os.path.exists(this.logFile):
            this.log = pd.DataFrame(columns=[col])
        else:
            this.log = pd.read_csv(this.logFile)
        this.last = this.data[col][len(this.data) - 1]
        this.now = getNow()
    
    def close (this):
        file = this.file
        this.data.loc[len(this.data)] = this.now
        this.data[-nKeep:].to_csv(file, index=False)
        
        if not os.path.exists(this.logPath): os.makedirs(this.logPath)
        this.log.loc[len(this.log)] = this.now
        this.log.to_csv(this.logFile, index=False)
        this.data = this.last = this.now = this.log = None

    

