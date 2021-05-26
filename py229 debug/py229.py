import sys, os, re
import traceback

class __LINE__(object):
    def __init__ (this, n=-4):
        this.n = n
    def __repr__(this):
        try:
            print (traceback.extract_stack()[this.n])
            a = traceback.extract_stack()[this.n]
            print (a.line, a.lineno, a.filename, a.name, a.locals)
            raise Exception
        except:
            
            print (len(traceback.extract_stack()))
            return str(sys.exc_info()[2].tb_frame.f_back.f_lineno)
    def __str__ (this): return repr(this)
 
__line__ = __LINE__()

try:
    print (__file__, __LINE__(-3))

    def ifDebug():
        return 0
        
        
    class debug:
        def __init__ (this):
            this.now = 0

        def __call__ (this, *args, **kw):
            tb = traceback.extract_stack()[-2]
            rst = re.findall(r'debug\((.*?)\)', tb.line)
            
            vars = rst[this.now]
            this.now += 1
            if this.now == len(rst): this.now = 0
            
            file = tb.filename
            line = tb.lineno
            
            vars = [x.strip() for x in vars.split(',')]
            
            
            if len(args): print(f'{file} line {line} :', ', '.join([f'{x} = {repr(y)}' for x, y in zip(vars, args)]), **kw)
    
    #def debug(*args, **kw):
    #    print (__file__, __line__, *args, **kw)
    
    if ifDebug():
        debug = debug()
    else:
        def debug (*args, **kw): pass
    
    debug('hh')
    
    a = 'hello world'
    
    
    debug(1,2), debug(), debug(3), debug(a)
except Exception as e:
    traceback.print_exc()
    raise e
finally:
    os.system('pause')