'''

建立学者索引

------------

esProject : 建立学者索引
'''

this = '学者'
thisEn = 'scholar'


import os, sys, re, json

from .tmpIncTable.tmpScholars import TmpScholars, table, idCol
from .cfg import nIdSep
from .getData.getScholarData import GetData, getActions, getHighLightActions
from .esBase import EsMainBase

index = f'landinn_{thisEn}'
indexHl = f'landinn_{thisEn}_highlight'

__path__  = os.path.dirname(os.path.abspath(__file__))

class EsScholar(EsMainBase):
    __version__ = 20210630
    __author__ = 'LymphV@163.com'

    def __init__ (self, this, thisEn, table, idCol, index, indexHl, TmpScholars, isAbroad=False):
        EsMainBase.__init__(self, this, thisEn, table, idCol, index, indexHl, TmpScholars)
        self.getData = GetData(this, thisEn, table, idCol, nIdSep)
        self.getActions = getActions
        self.getHighLightActions = getHighLightActions
        self.sizeBulk = 20
        self.isAbroad = isAbroad

esScholar = EsScholar(this, thisEn, table, idCol, index, indexHl, TmpScholars)
