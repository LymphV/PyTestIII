'''
生成所有时间窗口内更新的专利id的临时表
'''

if '.' in __name__:
    from .tmpTemplet import TmpTemplet, getSqlInsert
else:
    from tmpTemplet import TmpTemplet, getSqlInsert

tableTmpPatents = tableTmp = 'temp_db.tmp_patents'

### 0: 不含删除， 1: 含删除
sInsertBasic = [
    getSqlInsert(tableTmp, 'patent', 'golaxy_patent_id', containDel=0),
    getSqlInsert(tableTmp, 'patent', 'golaxy_patent_id'),
]

sInsert = [
    getSqlInsert(tableTmp, 'patent_abstracts', 'patent_id'),
    getSqlInsert(tableTmp, 'patent_applicants', 'patent_id', distinct=1),
    getSqlInsert(tableTmp, 'patent_authors', 'patent_id', distinct=1),
]


class TmpPatents (TmpTemplet):
    '''
    生成所有时间窗口内更新的专利id的临时表
    '''
    def __init__ (this, db, mode=0):
        'mode : 0-不含删除， 1-含删除'
        TmpTemplet.__init__(this)
        this.db = db
        this.tableTmp = tableTmp
        mode = 1 if mode else 0
        this.sInsert = [sInsertBasic[mode], *sInsert]
