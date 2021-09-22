'''
生成时间窗口内所有更新的专利id的临时表
'''

if '.' in __name__:
    from .tmpTemplet import TmpTemplet, getSqlInsert
else:
    from tmpTemplet import TmpTemplet, getSqlInsert

tableTmp = 'tmp_patents'

table = 'patent'
idCol = 'golaxy_patent_id'

### 0: 不含删除， 1: 含删除
sInsertBasic = [
    getSqlInsert(table, idCol, containDel=0),
    getSqlInsert(table, idCol, containDel=1),
]

sInsert = [
    getSqlInsert('patent_abstracts', 'patent_id',
        tableCheck=table, idColCheck=idCol),
    getSqlInsert('patent_applicants', 'patent_id', distinct=1,
        tableCheck=table, idColCheck=idCol),
    getSqlInsert('patent_authors', 'patent_id', distinct=1,
        tableCheck=table, idColCheck=idCol),
]


class TmpPatents (TmpTemplet):
    '''
    生成时间窗口内所有更新的专利id的临时表
    '''
    def __init__ (this, db, mode=0):
        'mode : 0-不含删除， 1-含删除'
        TmpTemplet.__init__(this)
        this.db = db
        this.tableTmpTemplet = tableTmp
        mode = 1 if mode else 0
        this.sInsert = [sInsertBasic[mode], *sInsert]
