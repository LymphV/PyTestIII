'''
生成时间窗口内所有更新的项目id的临时表
'''

if '.' in __name__:
    from .tmpTemplet import TmpTemplet, getSqlInsert
else:
    from tmpTemplet import TmpTemplet, getSqlInsert

tableTmp = 'tmp_projects'

table = 'project'
idCol = 'golaxy_project_id'

### 0: 不含删除， 1: 含删除
sInsertBasic = [
    getSqlInsert(table, idCol, containDel=0),
    getSqlInsert(table, idCol, containDel=1),
]


sInsert = [
    getSqlInsert('project_abstracts', 'project_id',
        tableCheck=table, idColCheck=idCol),
    getSqlInsert('project_authors', 'project_id', distinct=1,
        tableCheck=table, idColCheck=idCol),
]

class TmpProjects (TmpTemplet):
    '''
    生成时间窗口内所有更新的项目id的临时表
    '''
    def __init__ (this, db, mode=0):
        'mode : 0-不含删除， 1-含删除'
        TmpTemplet.__init__(this)
        this.db = db
        this.tableTmpTemplet = tableTmp
        mode = 1 if mode else 0
        this.sInsert = [sInsertBasic[mode], *sInsert]
