'''
if __name__ == '__main__':
    from a import f
else:
    from .a import f
'''
if __name__ == '__main__':
    from pkg.a import f
else:
    from .pkg.a import f

def main():
    f()

from pkg.pkg.x import y

if __name__ == '__main__':
    print ('main.py')
    y()
    main()