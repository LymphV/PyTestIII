'''
生成时间窗口内所有更新的国外学者id的临时表
'''


from .tmpScholars import TmpScholars


tableTmp = 'tmp_scholars_abroad'

table = 'authors_en'
idCol = 'golaxy_author_id'


class TmpScholarsAbroad (TmpScholars):
    '''
    生成时间窗口内所有更新的国外学者id的临时表
    '''
    def __init__ (this, db, table=table, idCol=idCol, tableTmpTemplet=tableTmp):
        TmpScholars.__init__(this, db, table, idCol, tableTmpTemplet, isAbroad=True)
