'''

建立论文索引

------------

esPaper : 建立论文索引
'''

this = '论文'
thisEn = 'paper'


import os, sys, re, json

from .getData.getPaperData import GetData, getActions
from .tmpIncTable.tmpPapers import TmpPapers, table, idCol
from .esBase import EsBase

index = f'landinn_{thisEn}'

class EsPaper(EsBase):
    __version__ = 20210625
    __author__ = 'LymphV@163.com'

    def __init__ (self, this, thisEn, table, idCol, index, TmpPapers):
        EsBase.__init__(self, this, thisEn, table, idCol, index, TmpPapers)
        self.getData = GetData(this, thisEn, table, idCol)
        self.getActions = getActions
        self.sizeBulk = 100

esPaper = EsPaper(this, thisEn, table, idCol, index, TmpPapers)
