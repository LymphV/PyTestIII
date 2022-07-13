'''
仅仅为了找一个真正的全局变量存储空间
'''


class VGlobals:
    '''
    仅仅为了找一个真正的全局变量存储空间
    
    可以再加功能
    '''

vGlobals = VGlobals()

import inspect

def getMainGlobals() -> dict:
    '''
    找到main空间的全局变量
    不如import __main__？
    对按Tab触发的importlib，调用栈里不存在交互环境的main空间，只会找到importlib的__main__
    '''
    cr = inspect.currentframe()
    while cr:
        if cr.f_globals.get('__name__', None) == '__main__':
            return cr.f_globals
        cr = cr.f_back
    return {}