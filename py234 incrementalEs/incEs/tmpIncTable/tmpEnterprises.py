'''
生成时间窗口内所有更新的企业id的临时表
'''

from .tmpTemplet import TmpTemplet, getSqlInsert, getSqlPublishInsert
from .tmpProducts import TmpProducts
from .tmpSoftwareCopyrights import TmpSoftwareCopyrights
from .tmpPatents import TmpPatents

from vMysql import stdSqlData

tableTmp = 'tmp_enterprises'

table = 'affiliations'
idCol = 'affiliation_id'

### 新增或更新基本信息的企业，不含删除企业
sInsert = [
    getSqlInsert(table, idCol, containDel=0, hasIsNew=1),
]

class TmpEnterprises (TmpTemplet):
    '''
    生成时间窗口内所有更新的企业id的临时表
    '''
    def __init__ (this, db):
        TmpTemplet.__init__(this)
        this.db = db
        this.tableTmpTemplet = tableTmp
        this.tmpPatents = None
        this.tmpSoftwareCopyrights = None
        this.tmpProducts = None

    def start (this, tLast, tNow):
        this.setTableTmp(tLast, tNow)
        this.db.sql(this.sCreate % this.tableTmp, ifCommit=True)

        db = this.db
        this.tmpPatents = TmpPatents(db, 1)
        this.tmpSoftwareCopyrights = TmpSoftwareCopyrights(db, 1)
        this.tmpProducts = TmpProducts(db, 1)

        this.tmpPatents.start(tLast, tNow)
        this.tmpSoftwareCopyrights.start(tLast, tNow)
        this.tmpProducts.start(tLast, tNow)

        tableTmpProducts = this.tmpPatents.tableTmp
        tableTmpSoftwareCopyrights = this.tmpSoftwareCopyrights.tableTmp
        tableTmpPatents = this.tmpProducts.tableTmp

        sInserts = [
            getSqlPublishInsert('patent_applicants', 'applicant_id', 'patent_id',
                tableTmpPatents, table, idCol, hasIsNew=1),
            getSqlPublishInsert('product', 'affiliation_id', 'golaxy_product_id',
                tableTmpProducts, table, idCol, hasIsNew=1),
            getSqlPublishInsert('softwareCopyright_affiliation', 'affiliation_id', 'sc_id',
                tableTmpSoftwareCopyrights, table, idCol, hasIsNew=1),
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
        if this.tmpSoftwareCopyrights is not None: this.tmpSoftwareCopyrights.close()
        if this.tmpProducts is not None: this.tmpProducts.close()
        this.db.sql(this.sRmTmp % this.tableTmp, ifCommit=True)
        this.ifStart = False
        this.tmpPatents = None
        this.tmpSoftwareCopyrights = None
        this.tmpProducts = None
