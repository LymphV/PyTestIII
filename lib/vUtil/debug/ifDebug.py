'''
设置运行时开启debug的逻辑

当前逻辑为在jupyter中开启调试，否则关闭调试
'''


def ifDebug():
    '''
    设置运行时开启debug的逻辑

    当前逻辑为在jupyter中开启调试，否则关闭调试
    '''
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
    return typeOfScript() == 'jupyter'