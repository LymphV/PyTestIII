'''
生成时间窗口内所有更新的学者id的临时表
'''

from .tmpTemplet import TmpTemplet, getSqlInsert, getSqlPublishInsert
from .tmpPapers import TmpPapers
from .tmpProjects import TmpProjects
from .tmpPatents import TmpPatents


from vMysql import stdSqlData

tableTmp = 'tmp_scholars'

table = 'authors'
idCol = 'golaxy_author_id'

class TmpScholars (TmpTemplet):
    '''
    生成时间窗口内所有更新的学者id的临时表
    '''
    def __init__ (this, db, table=table, idCol=idCol, tableTmpTemplet=tableTmp, isAbroad=False):
        TmpTemplet.__init__(this)
        this.db = db
        this.table = table
        this.idCol = idCol
        this.tableTmpTemplet = tableTmpTemplet
        this.tmpPatents = None
        this.tmpPapers = None
        this.tmpProjects = None
        this.isAbroad = isAbroad

    def start (this, tLast, tNow):
        this.setTableTmp(tLast, tNow)
        this.db.sql(this.sCreate % this.tableTmp, ifCommit=True)

        db = this.db
        this.tmpPatents = TmpPatents(db, 1)
        this.tmpPapers = TmpPapers(db, 1)
        this.tmpProjects = TmpProjects(db, 1)

        this.tmpPatents.start(tLast, tNow)
        this.tmpPapers.start(tLast, tNow)
        this.tmpProjects.start(tLast, tNow)

        tableTmpPapers = this.tmpPatents.tableTmp
        tableTmpProjects = this.tmpPapers.tableTmp
        tableTmpPatents = this.tmpProjects.tableTmp

        ### 新增或更新基本信息的学者，不含删除学者
        sInsert = [
            getSqlInsert(this.table, this.idCol, containDel=0, hasIsNew=1, isAbroad=this.isAbroad),
        ]

        sInserts = [
            getSqlPublishInsert('paper_author_affiliations', 'author_id', 'paper_id',
                tableTmpPapers, this.table, this.idCol, hasIsNew=1, isAbroad=this.isAbroad),
            getSqlPublishInsert('project_authors', 'author_id', 'project_id',
                tableTmpProjects, this.table, this.idCol, hasIsNew=1, isAbroad=this.isAbroad),
            getSqlPublishInsert('patent_authors', 'author_id', 'patent_id',
                tableTmpPatents, this.table, this.idCol, hasIsNew=1, isAbroad=this.isAbroad),
        ]

        tLast = stdSqlData(tLast)
        tNow = stdSqlData(tNow)
        for s in sInsert:
            db.sql(s % (this.tableTmp, tLast, tNow), ifCommit=True)
        for s in sInserts:
            db.sql(s % this.tableTmp, ifCommit=True)
        this.ifStart = True

    def close (this):
        if this.tmpPatents is not None: this.tmpPatents.close()
        if this.tmpPapers is not None: this.tmpPapers.close()
        if this.tmpProjects is not None: this.tmpProjects.close()
        this.db.sql(this.sRmTmp % this.tableTmp, ifCommit=True)
        this.ifStart = False
        this.tmpPatents = None
        this.tmpPapers = None
        this.tmpProjects = None
