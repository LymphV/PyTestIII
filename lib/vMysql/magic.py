'''
sql魔术命令
'''

__version__ = 20210608
__author__ = 'LymphV@163.com'

from .mysqlProxy import MysqlProxy

from IPython.core.magic import register_cell_magic, register_line_cell_magic

import atexit

db = None

def _closeDb ():
    if db is not None:
        db.close()

def _setDb (*args, **kwargs):
    '''
    设置魔术命令使用的db
    '''
    global db
    atexit.unregister(_closeDb)
    if db is not None: db.close()
    db = MysqlProxy(*args, **kwargs)
    atexit.register(_closeDb)

@register_cell_magic
def sql(line, cell):
    if db is None: _setDb()
    return db(cell) 