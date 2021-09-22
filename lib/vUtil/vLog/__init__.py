

import os
from vUtil.vTime import getToday, getNow
from vUtil.vFile import fprint

from vUtil.vTqdm import typeOfScript

__version__ = 20210727
__author__ = 'LymphV@163.com'


### 最大文件大小为10M
maxFileSize = 10 * (1 << 20)


_print = print

def frmt (*s, start='', tqdm=None, **k):
    if tqdm is None:
        _print (f'{start}({getNow()})', *s, **k)
    else:
        s = [f'{start}({getNow()})', *[str(x) for x in s]]
        tqdm.set_description(' '.join(s))

print = frmt

### jupyter内不影响variable inspector的运行
if typeOfScript == 'jupyter':
    import traceback, re
    
    cnt = 0
    def print (*x, **y):
        '''
        需要挂globals
        '''
        global cnt
        exs = traceback.extract_stack()
        
        rst = re.findall('<ipython-input-(\d+)-.+?>', exs[-2].filename)
        
        if not rst or 'globals' in print.__dict__ and f'_i{rst[0]}' in print.globals:
            frmt(*x, **y)
        else:
            if 'globals' not in print.__dict__: _print(*x, **y)
            else:
                if not cnt: _print(*x, **y)
                cnt = (cnt + 1) % 3 

def rootPath ():
    import traceback
    exs = traceback.extract_stack()
    rst = '.'
    for i in range(len(exs)):
        fileName = exs[-1 - i].filename.strip()
        if 'IPython' in fileName: break
        rst = fileName
    if rst.startswith('<') and rst.endswith('>'): rst = '.'
    rst = os.path.abspath(rst)
    return rst if os.path.isdir(rst) else os.path.dirname(rst)

rootPath = rootPath()


class VLog:
    def __init__ (this, file='log', path=os.path.join(rootPath, 'log'), sep=' : ', fileFormat='txt'):
        this.path = path
        this.file = file
        this.sep = sep
        this.fileFormat = fileFormat
        this.today = None
        this.no = 0
    
    def _getFileName (this):
        no = f'_{this.no}' if this.no else ''
        return f'{this.file}{this.today}{no}.{this.fileFormat}'
    
    
    def log (this, *s, mode='LOG', **k):
        path = this.path
        if not os.path.exists(path): os.makedirs(path)
        
        today = getToday()
        if this.today != today:
            this.today = today
            this.no = 0
        
        file = this._getFileName()
        filePath = os.path.join(path, file)
        while os.path.exists(filePath) and maxFileSize < os.path.getsize(filePath):
            this.no += 1
            file = this._getFileName()
            filePath = os.path.join(path, file)
        
        sep = k.get('sep', this.sep)
        k = {x : k[x] for x in k if x not in {'sep', 'file'}}
        
        fprint(f'[{mode}] ({getNow()})', file=file, path=path, end=' ')
        fprint(*s, **k, file=file, path=path, sep=sep)
    
    def err (this, *s, mode='ERROR', **k):
        this.log(*s, mode=mode, **k)
    
    def __call__ (this, *s, **k):
        return this.log(*s, **k)

class VError(VLog):
    def __init__ (this, file='error', path=os.path.join(rootPath, 'error'), sep=' : ', fileFormat='txt'):
        this.__class__.__base__.__init__(this, file, path, sep, fileFormat)
    
    def __call__ (this, *s, **k):
        return this.err(*s, **k)

vLog = VLog()
vError = VError()