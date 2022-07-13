import os

### 废除
#def fprint (s, file = 'out.txt', path = '.'):
#    if not os.path.exists(path): os.makedirs(path)
#    with open(os.path.join(path, file), 'a', encoding = 'utf-8') as f:
#        f.write(str(s))

def fprint (*x, file = 'out.txt', path = '.', **y):
    if not os.path.exists(path): os.makedirs(path)
    with open(os.path.join(path, file), 'a', encoding = 'utf-8') as f:
        print(*x, file=f, **y)
