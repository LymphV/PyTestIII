'''
生成所有时间窗口内更新的软著id的临时表
'''

if '.' in __name__:
    from .tmpTemplet import TmpTemplet, getSqlInsert
else:
    from tmpTemplet import TmpTemplet, getSqlInsert

tableTmpSoftwareCopyrights = tableTmp = 'temp_db.tmp_softwareCopyrights'


### 0: 不含删除， 1: 含删除
sInsertBasic = [
    getSqlInsert(tableTmp, 'software_copyright', 'golaxy_sc_id', containDel=0),
    getSqlInsert(tableTmp, 'software_copyright', 'golaxy_sc_id'),
]

sInsert = [
    getSqlInsert(tableTmp, 'softwareCopyright_affiliation', 'sc_id', distinct=1),
]

class TmpSoftwareCopyrights (TmpTemplet):
    '''
    生成所有时间窗口内更新的软著id的临时表
    '''
    def __init__ (this, db, mode=0):
        'mode : 0-不含删除， 1-含删除'
        TmpTemplet.__init__(this)
        this.db = db
        this.tableTmp = tableTmp
        mode = 1 if mode else 0
        this.sInsert = [sInsertBasic[mode], *sInsert]
