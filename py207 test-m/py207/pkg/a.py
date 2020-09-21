x = 1
y = 2

print (__name__)
from . import b

def f ():
    print ('pkg',x,y)
    b.g()
