'''

工具包

----------------------------

stdSqlData : 变量插入sql语句格式化
'''



def stdSqlData (s):
    '''
    变量插入sql语句格式化
    '''
    if s is None or s == '': return 'null'
    if type(s) in [list, dict, set]: s = str(s)
    return repr(s)
