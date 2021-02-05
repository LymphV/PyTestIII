'''

AminerPeterait工具包

----------------------------

stdAminerId : 去除id开头的'pid_'
typeOfScript : 判断脚本运行的环境
rmUnseen : 去除不可见字符
'''

import re
from vUtil.vTime import getNow


def stdAminerId (id):
    '''
    去除id开头的'pid_'
    '''
    return id[4:] if id.startswith('pid_') else id
    

def typeOfScript():
    '''
    判断脚本运行的环境
    '''
    try:
        ipy_str = str(type(get_ipython()))
        if 'zmqshell' in ipy_str:
            return 'jupyter'
        if 'terminal' in ipy_str:
            return 'ipython'
    except:
        return 'terminal'
        

def rmUnseen (s):
    '''
    去除不可见字符
    '''
    if s is None: return None
    return re.sub(r'\s+', ' ', str(s))

def frmt (*s, **k):
    print (f'({getNow()})', *s, **k)