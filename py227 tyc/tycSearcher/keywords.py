


if '.' in __name__:
    from .cfg import nMaxKeywords
else:
    from cfg import nMaxKeywords

from vMysql import MysqlProxy

table = '`landinn`.`keyword`'
updateCol = '`updated_tianyancha`'

__version__ = 20210831
__author__ = 'LymphV@163.com'

class Keywords:
    '''
    定义可迭代的关键词获取类
    '''
    
    def __len__ (this):
        db = MysqlProxy()
        rst = db.count(table, where=f'{updateCol} is null and not ifnull(is_deleted,0)')
        rst = rst.values.item()
        db.close()
        return min(nMaxKeywords, rst)
    
    def __bool__ (this):
        db = MysqlProxy()
        rst = db.count(table, nMaxKeywords, where=f'{updateCol} is null and not ifnull(is_deleted,0)')
        rst = rst.values.item()
        db.close()
        return bool(rst)
    
    
    def __iter__ (this):
        db = MysqlProxy()
        rst = db.select('*', table, nMaxKeywords, where=f'{updateCol} is null and not ifnull(is_deleted,0)')
        rst = rst['keyword'].to_list()
        db.close()
        return iter(rst)


### 可迭代的关键词列表
keywords = Keywords()

### 可使用自定义关键词列表，如
# keywords = ['摩擦力']