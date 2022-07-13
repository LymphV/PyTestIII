

import os, traceback, re, inspect
from typing import AnyStr
from vUtil.vTime import getToday, getNow
from vUtil.vFile import fprint

from vUtil.vTqdm import typeOfScript

import __main__  as main

__version__ = 20220630
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
    ### jupyter notebook variable inspector中print的字节码
    #   没有找到更好的特征
    #   之前使用临时文件名r'<ipython-input-(\d+)-.+?>中提取行号，对超范围行号判定为variable inspector
    #   但发现有r'/tmp/ipykernel_(\d+)/(\d+).py'的临时文件，无法提取行号
    #   故改为对调用字节码与下同的视为jupyter notebook variable inspector中的print
    bcodes = {
        b'e\x00e\x01\x83\x00\x83\x01F\x00d\x00S\x00'
    }

    
    cnt = 0
    def print (*x, **y):
        global cnt

        exs = traceback.extract_stack()
        rst = re.findall(r'<ipython-input-(\d+)-.+?>', exs[-2].filename)

        ### 调用print的frame的字节码
        bcode = inspect.currentframe().f_back.f_code.co_code

        if rst and hasattr(main, f'_i{rst[0]}') or bcode in bcodes:
            ### linux的variable inspector会执行3次，会抖动刷新，而windows似乎是28次
            if not cnt: _print(*x, **y)
            cnt = (cnt + 1) % 3 
        else:
            frmt(*x, **y)


### 防止（在按Tab时）被importlib加载
### 返回None后os.path.join会出错，导致importlib出错，真正import的时候会重新import，生成新的rootPath（从生成id的变化和__init__函数的运行次数可以验证）
class _RootPath:
    def __init__ (this):
        this.path = None
    def __eq__ (this, value: AnyStr or os.PathLike):
        return os.path.normcase(os.path.abspath(this)) == os.path.normcase(os.path.abspath(value))
    def __fspath__ (this):
        if this.path is None:
            ### 调用栈，python最底层是入口文件，ipython则有IPython包调用入口文件
            exs = traceback.extract_stack()
            
            ### frame，用于检测入口是否是importlib
            # frm = None

            ### ipython会在全局变量中存储入口目录
            try: dh = os.fspath(main._dh[0])
            except: dh = None

            rst = None

            ### cases
            #   jupyter交互 : dh，可cd
            #   ipython交互 : dh，可cd
            #   ipython文件 : 调用栈IPython调用的文件即入口文件，不可cd
            #   python交互  : 读到<stdin>，因此.，不可cd
            #   python文件  : 调用栈底部即入口文件，不可cd
            
            ### 是否处于交互模式，例如jupyter 或者python/ipython交互模式
            isInteractive = not hasattr(main, '__file__')
            if isInteractive and dh is not None:
                rst = dh
            else:
                rst = '.'
                for frame in reversed(exs):
                    filename = frame.filename.strip()
                    if 'IPython' in filename: break
                    rst = filename
                    # frm = frame
                ### 事实上可能有<stdin>、<ipython-input-x-x>和ipykernel_x\x.py三种格式，但因为已经被dh解决，所以没有补充后一种格式
                if rst.startswith('<') and rst.endswith('>'): rst = '.'
                
            rst = os.path.abspath(rst)
            
            this.path = rst if os.path.isdir(rst) else os.path.dirname(rst)
            ### 防止（在按Tab时）被importlib加载，事实上在使用import __main__后已无用
            # if frm is not None:
            #     fn = os.path.basename(frm.filename)
            #     pn = os.path.basename(os.path.dirname(frm.filename))
            #     if fn == '__init__.py' and pn == 'importlib' and frm.name == 'import_module':
            #         this.path = None
        return this.path
    __str__ = __repr__ = __fspath__

rootPath = _RootPath()


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
        return s
    
    def err (this, *s, mode='ERROR', **k):
        return this.log(*s, mode=mode, **k)
    
    def __call__ (this, *s, **k):
        return this.log(*s, **k)

class VError(VLog):
    def __init__ (this, file='error', path=os.path.join(rootPath, 'error'), sep=' : ', fileFormat='txt'):
        VLog.__init__(this, file, path, sep, fileFormat)
    
    def __call__ (this, *s, **k):
        return this.err(*s, **k)

vLog = VLog()
vError = VError()