'''

建立项目索引

------------

esProject : 建立项目索引
'''

this = '项目'
thisEn = 'project'

import os, sys, re, json

from .getData.getProjectData import GetData, getActions
from .tmpIncTable.tmpProjects import TmpProjects, table, idCol
from .esBase import EsBase

index = f'landinn_{thisEn}'

class EsProject(EsBase):
    __version__ = 20210625
    __author__ = 'LymphV@163.com'

    def __init__ (self, this, thisEn, table, idCol, index, TmpProjects):
        EsBase.__init__(self, this, thisEn, table, idCol, index, TmpProjects)
        self.getData = GetData(this, thisEn, table, idCol)
        self.getActions = getActions
        self.sizeBulk = 100

esProject = EsProject(this, thisEn, table, idCol, index, TmpProjects)
