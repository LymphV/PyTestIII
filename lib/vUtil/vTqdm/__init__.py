'''
vTqdm

根据当前运行环境
选择tqdm或者tqdm.notebook,
以及选择宽度
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

typeOfScript = typeOfScript()
ncols = tqdmNcols = 950 if typeOfScript == 'jupyter' else 120


if typeOfScript == 'jupyter':
    import tqdm.notebook as oriTqdm
else:
    import tqdm as oriTqdm


def tqdm (*x, ncols=ncols, **y):
    return oriTqdm.tqdm(*x, ncols=ncols, **y)

def trange(*x, ncols=ncols, **y):
    return oriTqdm.trange(*x, ncols=ncols, **y)