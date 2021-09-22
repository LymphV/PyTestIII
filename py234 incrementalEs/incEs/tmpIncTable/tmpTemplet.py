
from vMysql import stdSqlData

__version__ = 20210621
__author__ = 'LymphV@163.com'


### 临时表schema
dbTmp = 'temp_db'

sCreate = '''
create table if not exists %s
(id bigint not null, primary key (id));
'''

sRmTmp = '''
drop table if exists %s;
'''


def getSqlInsert (table, idCol, containDel=1, hasIsNew=0, distinct=0, tableCheck=None, idColCheck=None):
    if tableCheck is None or idColCheck is None:
        return f'''
        replace into %s
        (
        	select {'distinct' if distinct else ''} {idCol} as id from {table}
            where %s <= ifnull (updated_at, created_at)
                and ifnull (updated_at, created_at) < %s
                {'' if containDel else 'and not is_deleted'}
                {'and not is_new' if hasIsNew else ''}
        );
        '''

    ### 关系表里被删除的id如果id本身没有被删除应该被视为更新
    ### 此时containDel字段无效
    return f'''
    replace into %s
    (
        select id
        from
        (
            select {'distinct ' if distinct else ''}{idCol} as id from {table}
            where %s <= ifnull (updated_at, created_at)
                and ifnull (updated_at, created_at) < %s
        ) as a
        join {tableCheck} as b
        on a.id = b.{idColCheck}
        and not b.is_deleted
        {'and not b.is_new' if hasIsNew else ''}
    );
    '''

def getSqlPublishInsert (tableRelation, idColRelation, pidColRelation,
        tableTmpPublish, table, idCol, hasIsNew=0):
    '''
    插入成果更新的学者/企业id

    Parameters
    ----------
    tableTmp : 学者/企业id临时表
    tableRelation : 学者/企业成果关系表
    idColRelation : 学者/企业成果关系表学者/企业id列
    pidColRelation : 学者/企业成果关系表成果id列
    tableTmpPublish : 成果id临时表
    table : 学者/企业表
    idCol : 学者/企业表id列
    hasIsNew : 是否含有is_new字段，is_new=1不进行索引
    '''
    return f'''
    replace into %s
    (
        select id
        from
        (
            select distinct {idColRelation} as id
            from {tableRelation} as a
            join {tableTmpPublish} as b
            on a.{pidColRelation} = b.id
        ) as c
        join {table} as d
        on c.id = d.{idCol}
        where !ifnull(d.is_deleted, 0)
        {'and !ifnull(d.is_new, 0)' if hasIsNew else ''}
    );
    '''


class TmpTemplet:
    '''
    生成时间窗口内更新的所有某种id的临时表

    需要
    this.db : 数据库连接，MysqlProxy对象
    this.tableTmpTemplet : 临时表名模板
    this.sInsert : 临时表插入语句列表
    '''
    def __init__ (this):
        this.sCreate = sCreate
        this.sRmTmp = sRmTmp
        this.ifStart = False

    def __len__ (this):
        if not this.ifStart: return 0
        return this.db.count(this.tableTmp).values.item()

    def setTableTmp (this, tLast, tNow):
        this.tableTmpName = this.tableTmpTemplet + f'({tLast},{tNow})%d'
        i = 0
        while 1:
            t = this.tableTmpName % i
            if this.checkTableTmp(t):
                i += 1
            else:
                this.tableTmpName = t
                break
        this.tableTmp = f'`{dbTmp}`.`{this.tableTmpName}`'

    def checkTableTmp (this, t=None):
        if t is None: t = this.tableTmpName
        where = f'table_schema={stdSqlData(dbTmp)} and table_name={stdSqlData(t)}'
        rst = this.db.select('*', 'information_schema.TABLES', where=where)
        return 0 < len(rst)

    def start (this, tLast, tNow):
        this.setTableTmp(tLast, tNow)
        this.db.sql(this.sCreate % this.tableTmp, ifCommit=True)

        tLast = stdSqlData(tLast)
        tNow = stdSqlData(tNow)
        for s in this.sInsert:
            this.db.sql(s % (this.tableTmp, tLast, tNow), ifCommit=True)
        this.ifStart = True

    def close (this):
        this.db.sql(this.sRmTmp % this.tableTmp, ifCommit=True)
        this.ifStart = False
