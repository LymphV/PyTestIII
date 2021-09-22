
import os

if '.' in __name__:
    from .timeManager import TimeManager
    from .cfg import mysqlDb, table, timeCol, flagCol
else:
    from timeManager import TimeManager
    from cfg import mysqlDb, table, timeCol, flagCol

from vMysql import MysqlProxy, stdSqlCol, stdSqlData

class TimeManagerMysql(TimeManager):
    '''
    TimeManagerMysql

    -----------

    管理更新时间
    TimeManagerMysql.last : 上次更新时间
    TimeManagerMysql.now : 本次更新时间

    TimeManagerMysql.start : 启动，读取本次更新时间
    TimeManagerMysql.close : 关闭，保存本次更新时间
    '''

    __version__ = 20210826
    __author__ = 'LymphV@163.com'

    def __init__ (this, table=table, timeCol=timeCol, flagCol=flagCol, db=mysqlDb):
        TimeManager.__init__(this)
        this.db = MysqlProxy(db=db)
        this.table = table
        this.timeCol = timeCol
        this.flagCol = flagCol

    def check (this):
        '''
        检测，是否有有效的当前时间
        '''
        now = this.db.select(timeCol, table, 1, where=f'not {flagCol}', order=f'by {timeCol} desc')
        return 0 < len(now)

    def start (this):
        '''
        启动，读取本次更新时间
        '''
        table = stdSqlCol(this.table)
        timeCol = stdSqlCol(this.timeCol)
        flagCol = stdSqlCol(this.flagCol)

        this.last = str(this.db.select(timeCol, table, 1, where=flagCol, order=f'by {timeCol} desc')[this.timeCol][0])
        this.now = str(this.db.select(timeCol, table, 1, where=f'not {flagCol}', order=f'by {timeCol} desc')[this.timeCol][0])
        this.db.close()

    def close (this):
        '''
        关闭，保存本次更新时间
        '''
        table = stdSqlCol(this.table)
        timeCol = stdSqlCol(this.timeCol)
        flagCol = stdSqlCol(this.flagCol)

        this.db.sql(f'''
            update {table}
            set {flagCol} = 1
            where not {flagCol}
            and {timeCol} <= {stdSqlData(this.now)}
        ''', ifCommit=True)
        this.last = this.now = None
        this.db.close()
