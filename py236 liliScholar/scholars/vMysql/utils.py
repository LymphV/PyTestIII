'''

工具包

----------------------------

stdSqlData : 变量插入sql语句格式化
stdSqlCol : 列名插入sql语句格式化
'''



def stdSqlData (s):
    '''
    变量插入sql语句格式化
    '''
    if s is None or s == '': return 'null'
    if type(s) in [list, dict, set]: s = str(s)
    return repr(s)

def stdSqlCol (s):
    '''
    列名插入sql语句格式化
    '''
    if not isinstance(s, str): return '``'
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