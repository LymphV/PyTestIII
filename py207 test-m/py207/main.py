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

if __name__ == '__main__':
    print ('main.py')
    main()