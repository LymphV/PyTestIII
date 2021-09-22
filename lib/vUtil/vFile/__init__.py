import os

### 废除
#def fprint (s, file = 'out.txt', path = '.'):
#    if not os.path.exists(path): os.makedirs(path)
#    with open(os.path.join(path, file), 'a', encoding = 'utf-8') as f:
#        f.write(str(s))

def fprint (*x, file = 'out.txt', path = '.', mode='a', **y):
    if not os.path.exists(path): os.makedirs(path)
    with open(os.path.join(path, file), mode, encoding = 'utf-8') as f:
        print(*x, file=f, **y)

def readlines (f, nLine):
    rst = []
    for i in range(nLine):
        s = f.readline()
        if not s: break
        rst += [s]
    return rst


def linesReader (file, nLine=1):
    if type(file) is str:
        with open(file) as f:
            for x in linesReader(f, nLine):
                yield x
    else:
        while 1:
            rst = readlines(file, nLine)
            if rst: yield rst
            else: break