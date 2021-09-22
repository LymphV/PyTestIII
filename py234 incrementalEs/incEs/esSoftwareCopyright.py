'''

建立软著索引

------------

esSoftwareCopyright : 建立软著索引
'''

this = '软著'
thisEn = 'software_copyright'

import os, sys, re, json

from .getData.getSoftwareCopyrightData import GetData, getActions
from .tmpIncTable.tmpSoftwareCopyrights import TmpSoftwareCopyrights, table, idCol
from .esBase import EsBase

index = f'landinn_{thisEn}'

class EsSoftwareCopyright(EsBase):
    __version__ = 20210625
    __author__ = 'LymphV@163.com'

    def __init__ (self, this, thisEn, table, idCol, index, TmpSoftwareCopyrights):
        EsBase.__init__(self, this, thisEn, table, idCol, index, TmpSoftwareCopyrights)
        self.getData = GetData(this, thisEn, table, idCol)
        self.getActions = getActions
        self.sizeBulk = 100

esSoftwareCopyright = EsSoftwareCopyright(this, thisEn, table, idCol, index, TmpSoftwareCopyrights)
