'''
生成所有时间窗口内更新的企业id的临时表
'''
if '.' in __name__:
    from .utils import stdSqlData
    from .tmpProducts import tableTmpProducts, TmpProducts
    from .tmpSoftwareCopyrights import tableTmpSoftwareCopyrights, TmpSoftwareCopyrights
    from .tmpPatents import tableTmpPatents, TmpPatents
    from .tmpTemplet import TmpTemplet, getSqlInsert, getSqlPublishInsert
else:
    from utils import stdSqlData
    from tmpProducts import tableTmpProducts, TmpProducts
    from tmpSoftwareCopyrights import tableTmpSoftwareCopyrights, TmpSoftwareCopyrights
    from tmpPatents import tableTmpPatents, TmpPatents
    from tmpTemplet import TmpTemplet, getSqlInsert, getSqlPublishInsert

tableTmpEnterprises = tableTmp = 'temp_db.tmp_enterprises'

### 新增或更新基本信息的企业，不含删除企业
sInsert = [
    getSqlInsert(tableTmp, 'affiliations', 'affiliation_id', containDel=0),
]

sInserts = [
    getSqlPublishInsert(tableTmp, 'patent_applicants', 'applicant_id', tableTmpPatents, 'patent_id'),
    getSqlPublishInsert(tableTmp, 'product', 'affiliation_id', tableTmpProducts, 'golaxy_product_id'),
    getSqlPublishInsert(tableTmp, 'softwareCopyright_affiliation', 'affiliation_id', tableTmpSoftwareCopyrights, 'sc_id'),
]

class TmpEnterprises (TmpTemplet):
    '''
    生成所有时间窗口内更新的企业id的临时表
    '''
    def __init__ (this, db):
        TmpTemplet.__init__(this)
        this.db = db
        this.tableTmp = tableTmp
        this.tmpPatents = None
        this.tmpSoftwareCopyrights = None
        this.tmpProducts = None

    def start (this, tLast, tNow):
        this.close()

        db = this.db
        this.tmpPatents = TmpPatents(db, 1)
        this.tmpSoftwareCopyrights = TmpSoftwareCopyrights(db, 1)
        this.tmpProducts = TmpProducts(db, 1)
        db.sql(this.sCreate % this.tableTmp, ifCommit=True)

        this.tmpPatents.start(tLast, tNow)
        this.tmpSoftwareCopyrights.start(tLast, tNow)
        this.tmpProducts.start(tLast, tNow)

        tLast = stdSqlData(tLast)
        tNow = stdSqlData(tNow)
        for s in sInsert:
            db.sql(s % (tLast, tNow), ifCommit=True)
        for s in sInserts:
            db.sql(s, ifCommit=True)
        this.ifStart = True

    def close (this):
        if this.tmpPatents: this.tmpPatents.close()
        if this.tmpSoftwareCopyrights: this.tmpSoftwareCopyrights.close()
        if this.tmpProducts: this.tmpProducts.close()
        this.db.sql(this.sRmTmp % this.tableTmp, ifCommit=True)
        this.ifStart = False
        this.tmpPatents = None
        this.tmpSoftwareCopyrights = None
        this.tmpProducts = None
