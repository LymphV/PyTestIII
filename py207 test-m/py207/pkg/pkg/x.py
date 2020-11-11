
#wrong!!会引外部的y
'''
try:
    from y import y
except ImportError:
    from .y import y
    '''

if '.' in __name__:
    print (__name__)
    from .y import y
else:
    from y import y
