'''
CountManager

-----------

管理关键词计数
CountManager.data : 关键词计数

CountManager.add : 添加关键词和计数
CountManager.close : 关闭，保存关键词和计数
'''

import pandas as pd, numpy as np
import os
from vUtil.vTime import getNow, getToday


defPath = r'countManager'
defFile = r'%s.csv'
cols = ['keyword', 'time', 'count', 'validCount']


__path__  = os.path.dirname(os.path.abspath(__file__))

class CountManager:
    '''
    CountManager

    -----------

    管理关键词计数
    CountManager.data : 关键词计数

    CountManager.add : 添加关键词和计数
    CountManager.close : 关闭，保存关键词和计数
    '''
    
    __version__ = 20210830
    __author__ = 'LymphV@163.com'
    
    def initCount (*args):
        return np.array([0,0])

    def __init__ (this, file=None, path=None):
        this.data = None
        file = defFile % getToday() if file is None else file
        path = defPath if path is None else path
        path = os.path.join(__path__, path)
        if not os.path.exists(path): os.makedirs(path)
        
        this.file = os.path.join(path, file)
        this.start()
    
    def start (this):
        file = this.file
        if not os.path.exists(file):
            this.data = pd.DataFrame(columns=cols)
            this.data.loc[0] = ['', getNow(), 0, 0]
        else:
            this.data = pd.read_csv(file)
    
    def add (this, keyword, count):
        if this.data is None: return
        this.data.loc[len(this.data)] = [keyword, getNow(), *count]
        totC = this.data['count'][0] + count[0]
        totVc = this.data['validCount'][0] + count[1]
        this.data.loc[0] = ['', getNow(), totC, totVc]
    
    def close (this):
        file = this.file
        if not this.data.empty: this.data.to_csv(file, index=False)
        this.data = None

    

