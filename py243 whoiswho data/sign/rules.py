from pypinyin import pinyin, Style
from itertools import permutations

from .utils import makeMatch, makeStd, isShort

from vUtil.vLang import countChinese, hasChinese

class SignRule:
    def __init__ (this, rule, rst=None):
        if rst is None: rst = {}
        this.rule = rule
        this.lastRule = None
        this.rst = rst
    
    def addName (this, name, rule=None):
        if rule is None: rule = this.rule
        if this.lastRule: rule = this.lastRule + '/' + rule
        if name not in this.rst:
            this.rst[name] = rule
            
    def makeRule (this, *rules):
        return '_'.join(rules)
    
    def solve (this, names):
        for name, rule in [*names.items()]:
            this.addName(name, rule)
            this.lastRule = rule
            this.solveOne(name, rule)
            this.lastRule = None
        return this.rst
    
    def dfs (this, arr, i = 0, rst=[]):
        if i == len(arr):
            yield rst
            return
        for x in arr[i]:
            for y in this.dfs(arr, i + 1, [*rst, x]):
                yield y
    __call__ = solve

class RuleC2e(SignRule):
    def __init__ (this, rst=None):
        rule = 'c2e'
        SignRule.__init__(this, rule, rst)
        rule2sur = '2sur'
        ruleHyphen = 'hyphen'
        
        this.rule2sur = this.makeRule(rule, rule2sur)
        this.ruleHyphen = this.makeRule(rule, ruleHyphen)
        this.rule2surHyphen = this.makeRule(rule, rule2sur, ruleHyphen)
    
    def solveOne (this, name, rule=None):
        if not hasChinese(name): return this.rst
        pys = pinyin(name, style=Style.NORMAL, heteronym=True)
        pys = [[y.capitalize() for y in x] for x in pys]
        
        for x in this.dfs(pys):
            this.addName(x[0] + ' ' + '-'.join(x[1:]), this.ruleHyphen)
            this.addName(x[0] + ' ' + ''.join(x[1:]))
            
            ### 复姓
            if 2 < len(x):
                this.addName('-'.join(x[:2]) + ' ' + '-'.join(x[2:]), this.rule2surHyphen)
                this.addName('-'.join(x[:2]) + ' ' + ''.join(x[2:]), this.rule2surHyphen)
                this.addName(''.join(x[:2]) + ' ' + '-'.join(x[2:]), this.rule2surHyphen)
                this.addName(''.join(x[:2]) + ' ' + ''.join(x[2:]), this.rule2sur)
        return this.rst

class RuleSwap(SignRule):
    def __init__ (this, rst=None):
        rule = 'swap'
        SignRule.__init__(this, rule, rst)
    
    def solveOne (this, name, rule=None):
        for x in permutations(name.split()):
            if isShort(x[-1]): continue
            this.addName(' '.join(x))
        return this.rst

class RuleMid(SignRule):
    def __init__ (this, rst=None):
        rule = 'mid'
        SignRule.__init__(this, rule, rst)
    
    def solveOne (this, name, rule=None):
        '''
        如果不小心把middle name分成两个词，也应该是不改变顺序的才是有效的middle name
        '''
        rst = name.split()
        if 2 < len(rst):
            for i in range(1, len(rst) - 1):
                for j in range(i + 1, len(rst)):
                    this.addName(' '.join(rst[:i] + rst[j:]))
        return this.rst

class RuleHyphen(SignRule):
    def __init__ (this, rst=None):
        rule = 'rmhy'
        SignRule.__init__(this, rule, rst)
    
    def rmhy (this, s):
        return [s, s.replace('-', '')] if '-' in s else [s]

    def solveOne (this, name, rule=None):
        rms = [this.rmhy(x) for x in name.split()]
        for x in this.dfs(rms):
            this.addName(' '.join(x))
        return this.rst

class RuleShort(SignRule):
    '''
    最末词不缩写
    '''
    def __init__ (this, rst=None):
        rule = 'short'
        SignRule.__init__(this, rule, rst)
        
    def short (this, s):
        if isShort(s): return [s]
        rst = [s, s[0] + '.']
        if '-' in s:
            rst += ['-'.join(x[0] + '.' for x in s.split('-'))]
        return rst
    
    def solveOne (this, name, rule=None):
        shorts = [this.short(x) for x in name.split()[:-1]] + [[name.split()[-1]]]
        for x in this.dfs(shorts):
            this.addName(' '.join(x))
        return this.rst