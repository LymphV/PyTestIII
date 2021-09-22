'''

建立专利索引

------------

esPatent : 建立专利索引
'''

this = '专利'
thisEn = 'patent'

import os, sys, re, json


from .getData.getPatentData import GetData, getActions
from .tmpIncTable.tmpPatents import TmpPatents, table, idCol
from .esBase import EsBase

index = f'landinn_{thisEn}'

class EsPatent(EsBase):
    __version__ = 20210625
    __author__ = 'LymphV@163.com'

    def __init__ (self, this, thisEn, table, idCol, index, TmpPatents):
        EsBase.__init__(self, this, thisEn, table, idCol, index, TmpPatents)
        self.getData = GetData(this, thisEn, table, idCol)
        self.getActions = getActions
        self.sizeBulk = 100

esPatent = EsPatent(this, thisEn, table, idCol, index, TmpPatents)
