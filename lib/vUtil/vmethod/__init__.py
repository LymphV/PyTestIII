'''
vmethod

普通method与classmethod的结合体

例如类定义了默认值，从类调用函数时使用该默认值，但从类实例调用时可以修改该默认值

class A:
    a = 1
    def __init__ (this, a=None):
        if a is not None: this.a = a
            
    @vmethod
    def f(this):
        return this.a

>> A.f()
1
>> A().f()
1
>> A(2).f()
2

'''


class vmethod:
    def __init__ (this, f):
        this.f = f
    def __call__ (this, self, /, *args, **kwargs):
        '''
        仅针对类内使用的时候可以不写
        '''
        return this.f(self, *args, kwargs)
    def __get__ (this, instance, owner):
        return this.f.__get__(owner if instance is None else instance, owner)