'''
vTqdm

根据当前运行环境
选择tqdm或者tqdm.notebook,
以及选择宽度
'''

__version__ = 20220331
__author__ = 'LymphV@163.com'

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

typeOfScript = typeOfScript()
ncols = tqdmNcols = 950 if typeOfScript == 'jupyter' else 120

def newTqdmClose (tqdm):
    try:
        tqdm.oldClose
        return
    except AttributeError: pass

    tqdm.oldClose = tqdm.close
    def newClose (this, *args, **kwargs):
        this.container.close()
        if not this.leave: return
        format_dict = dict(this.format_dict)
        format_dict['bar_format'] = '{l_bar}{r_bar}'
        print(this.format_meter(**format_dict))
    tqdm.newClose = newClose
    
    def tqdmClose (this, *args, **kwargs):
        rst = this.oldClose()
        this.newClose()
        this.newClose = lambda *args, **kwargs: None
        return rst
    tqdm.close = tqdmClose

if typeOfScript == 'jupyter':
    import tqdm.notebook as oriTqdm
    import tqdm as terminalTqdm
    newTqdmClose(oriTqdm.tqdm)
    
else:
    import tqdm as oriTqdm
    import tqdm as terminalTqdm

def setMode (s):
    global oriTqdm
    if s == 'jupyter':
        import tqdm.notebook as oriTqdm
        newTqdmClose(oriTqdm.tqdm)
    else:
        import tqdm as oriTqdm
    


def tqdm (*x, ncols=ncols, terminal=False, **y):
    return terminalTqdm.tqdm(*x, ncols=ncols, **y) if terminal else oriTqdm.tqdm(*x, ncols=ncols, **y)

def trange(*x, ncols=ncols, terminal=False, **y):
    return terminalTqdm.trange(*x, ncols=ncols, **y) if terminal else oriTqdm.trange(*x, ncols=ncols, **y)