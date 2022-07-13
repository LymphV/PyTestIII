
if '.' in __name__:
    from .utils import stdSqlData
else:
    from utils import stdSqlData

sCreate = '''
create table if not exists %s
(id bigint not null, primary key (id));
'''

sRmTmp = '''
drop table if exists %s;
'''

def getSqlInsert (tableTmp, table, idCol, containDel=1, distinct=0):
    return f'''
    replace into {tableTmp}
    (
    	select {'distinct' if distinct else ''} {idCol} as id from {table}
        where %s <= ifnull (updated_at, created_at)
            and ifnull (updated_at, created_at) < %s
            {'' if containDel else 'and !ifnull(is_deleted, 0)'}
    );
    '''

def getSqlPublishInsert (tableTmp, table, idCol, tableTmpPublish, pidCol):
    return f'''
    replace into {tableTmp}
    (
        select distinct {idCol} as id
        from {table} as a
        join {tableTmpPublish} as b
        on a.{pidCol} = b.id
    );
    '''

class TmpTemplet:
    '''
    生成所有时间窗口内更新的某种id的临时表

    需要
    this.db : 数据库连接，MysqlProxy对象
    this.tableTmp : 临时表名
    this.sInsert : 临时表插入语句列表
    '''
    def __init__ (this):
        this.sCreate = sCreate
        this.sRmTmp = sRmTmp
        this.ifStart = False

    def __len__ (this):
        if not this.ifStart: return 0
        return this.db.count(this.tableTmp).values.item()

    def start (this, tLast, tNow):
        this.close()

        this.db.sql(this.sCreate % this.tableTmp, ifCommit=True)
        tLast = stdSqlData(tLast)
        tNow = stdSqlData(tNow)
        for s in this.sInsert:
            this.db.sql(s % (tLast, tNow), ifCommit=True)
        this.ifStart = True

    def close (this):
        this.db.sql(this.sRmTmp % this.tableTmp, ifCommit=True)
        this.ifStart = False
