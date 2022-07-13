'''

工具包

----------------------------

isNull : 判断变量是否视为null
stdSqlData : 变量插入sql语句格式化
stdSqlCol : 列名插入sql语句格式化
'''

import pandas as pd

from pymysql.converters import escape_string
from collections.abc import Sized

def isNull (s):
    '''
    判断变量是否视为null
    
    pd.isna可以检测float('nan'), math.nan, np.nan, None, pd.NaT, pd.NA，视为null
    并且'', []视为null
    '''
    return len(s) == 0  if isinstance(s, Sized) else pd.isna(s)


def stdSqlData (s, db=None, remain=False):
    '''
    变量插入sql语句格式化
    '''
    if not remain:
        if isinstance(s, str): s = s.strip()
        if isNull(s): return 'null'
    else:
        if s is None: return 'null'
    if isinstance(s, (list, dict, set)): s = str(s)
    
    try:
        if db is None:
            return "'" + escape_string(s) + "'"
        return db.escape(s)
    except (TypeError, AttributeError):
        return repr(s)

def stdSqlCol (s):
    '''
    列名插入sql语句格式化
    '''
    if not isinstance(s, str): return '``'
    s = s.strip()
    if s.startswith('`') and s.endswith('`'): return s
    
    rst = []
    for x in s.split('.'):
        x = x.strip()
        if '*' in x or '(' in x or ')' in x:
            rst += [x]
            continue
        if x.startswith('`'): x = x[1:]
        if x.endswith('`'): x = x[:-1]
        rst += [f'`{x}`']
    
    return '.'.join(rst) 