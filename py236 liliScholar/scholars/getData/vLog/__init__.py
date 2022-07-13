

import os
from .vTime import getToday, getNow
from .vFile import fprint


def frmt (*s, start='', tqdm=None, **k):
    if tqdm is None:
        print (f'{start}({getNow()})', *s, **k)
    else:
        s = [f'{start}({getNow()})', *[str(x) for x in s]]
        tqdm.set_description(' '.join(s))

class VLog:
    def __init__ (this, file='log', path='log', sep=' : ', fileFormat='txt'):
        this.path = path
        this.file = file
        this.sep = sep
        this.fileFormat = fileFormat
    
    def log (this, *s, mode='LOG', **k):
        path = this.path
        file = f'{this.file}{getToday()}.{this.fileFormat}'
        sep = k.get('sep', this.sep)
        k = {x : k[x] for x in k if x not in {'sep', 'file'}}
        if not os.path.exists(path): os.makedirs(path)
        fprint(f'[{mode}] ({getNow()})', file=file, path=path, end=' ')
        fprint(*s, **k, file=file, path=path, sep=sep)
    
    def err (this, *s, mode='ERROR', **k):
        this.log(*s, mode=mode, **k)
    
    def __call__ (this, *s, **k):
        return this.log(*s, **k)

class VError(VLog):
    def __init__ (this, file='error', path='error', sep=' : ', fileFormat='txt'):
        this.__class__.__base__.__init__(this, file, path, sep, fileFormat)
    
    def __call__ (this, *s, **k):
        return this.err(*s, **k)