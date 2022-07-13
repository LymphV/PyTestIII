
### 临时表schema
dbTmp = 'temp_db'

class ViewAll:
    '''
    生成所有的有效的某种id的视图

    this.start : 创建或替换视图
    this.close : 关闭（不删除视图）

    '''
    __version__ = 20210630
    __author__ = 'LymphV@163.com'
    
    def __init__ (this, db, thisEn, table, idCol, hasIsNew=False):
        '''
        生成所有的有效的某种id的视图

        Parameters
        ----------
        db : MysqlProxy，数据库连接
        thisEn : 英文
        table : 表名
        idCol : 表id列
        hasIsNew : 是否含有is_new字段
        '''
        this.db = db
        this.ifStart = False

        this.sCreate = f'''
            create or replace view `{dbTmp}`.`tmp_lymphv_{thisEn}`
            as select {idCol} as id from {table}
            where not ifnull(is_deleted,0)
            {'and not ifnull(is_new,0)' if hasIsNew else ''};
        '''
        this.tableTmp = f'`{dbTmp}`.`tmp_lymphv_{thisEn}`'

    def __len__ (this):
        if not this.ifStart: return 0
        return this.db.count(this.tableTmp).values.item()

    def start (this, *_):
        this.db.sql(this.sCreate, ifCommit=True)
        this.ifStart = True

    def close (this):
        this.ifStart = False
