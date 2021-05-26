if '.' in __name__:
    from .n500k.n5 import names
else:
    from n500k.n5 import names

#names = names1 + names2