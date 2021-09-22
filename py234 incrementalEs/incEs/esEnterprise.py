'''

建立企业索引

------------

esEnterprise : 建立企业索引
'''

this = '企业'
thisEn = 'enterprise'

import os, sys, re, json

from .tmpIncTable.tmpEnterprises import TmpEnterprises, table, idCol
from .cfg import nIdSep
from .getData.getEnterpriseData import GetData, getActions, getHighLightActions
from .esBase import EsMainBase

index = f'landinn_{thisEn}'
indexHl = f'landinn_{thisEn}_highlight'

__path__  = os.path.dirname(os.path.abspath(__file__))


class EsEnterprise(EsMainBase):
    __version__ = 20210727
    __author__ = 'LymphV@163.com'

    def __init__ (self, this, thisEn, table, idCol, index, indexHl, TmpEnterprises):
        EsMainBase.__init__(self, this, thisEn, table, idCol, index, indexHl, TmpEnterprises)
        self.getData = GetData(this, thisEn, table, idCol, nIdSep)
        self.getActions = getActions
        self.getHighLightActions = getHighLightActions
        self.sizeBulk = 20

esEnterprise = EsEnterprise(this, thisEn, table, idCol, index, indexHl, TmpEnterprises)
