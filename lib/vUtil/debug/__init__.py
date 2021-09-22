'''
debug

---------------

debug功能，显示文件名、行号、变量名


在ifDebug.py中设置运行时开启debug的逻辑，当前逻辑为在jupyter中开启调试，否则关闭调试

debug : callable调试对象，用法同print，显示文件名、行号、变量名

用法:
-----

if '.' in __name__:
    from .debug import debug
else:
    from debug import debug

a = 1
b = 'hello world'
debug(a, b)
'''


import sys, os, re
import traceback

from .ifDebug import ifDebug

__version__ = 20210623
__author__ = 'LymphV@163.com'

class debug:
    '''
    debug

    ---------------

    debug功能，显示文件名、行号、变量名

    在ifDebug.py中设置运行时开启debug的逻辑，当前逻辑为在jupyter中开启调试，否则关闭调试

    debug : callable调试对象，用法同print，显示文件名、行号、变量名
    '''

    def __init__ (this):
        this.now = 0

    def __call__ (this, *args, **kw):
        '''用法同print，显示文件名、行号、变量名'''
        tb = traceback.extract_stack()[-2]
        rst = re.findall(r'debug\((.*?)\)', tb.line)
        
        vars = rst[this.now]
        this.now += 1
        if this.now == len(rst): this.now = 0
        
        file = tb.filename
        line = tb.lineno
        
        vars = [x.strip() for x in vars.split(',')]
        
        if len(args): print(f'{file} line {line} :', ', '.join([f'{x} = {repr(y)}' for x, y in zip(vars, args)]), **kw)

    @property
    def file (this):
        return traceback.extract_stack()[-2].filename
    
    @property
    def line (this):
        return traceback.extract_stack()[-2].line
    
    @property
    def lineno (this):
        return traceback.extract_stack()[-2].lineno
    
if ifDebug():
    debug = debug()
else:
    debug.__call__ = lambda *x, **y: None
    debug = debug()