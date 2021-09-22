'''

建立产品索引

------------

esProduct : 建立产品索引
'''

this = '产品'
thisEn = 'product'


import os, sys, re, json

from .tmpIncTable.tmpProducts import TmpProducts, table, idCol
from .getData.getProductData import GetData, getActions
from .esBase import EsBase

index = f'landinn_{thisEn}'

class EsProduct(EsBase):
    __version__ = 20210625
    __author__ = 'LymphV@163.com'

    def __init__ (self, this, thisEn, table, idCol, index, TmpProducts):
        EsBase.__init__(self, this, thisEn, table, idCol, index, TmpProducts)
        self.getData = GetData(this, thisEn, table, idCol)
        self.getActions = getActions
        self.sizeBulk = 100

esProduct = EsProduct(this, thisEn, table, idCol, index, TmpProducts)
