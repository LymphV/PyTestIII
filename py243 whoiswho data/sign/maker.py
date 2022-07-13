
from .rules import RuleC2e, RuleSwap, RuleMid, RuleHyphen, RuleShort

from .utils import makeMatch, makeStd, isShort

class SignMaker:
    '''
    署名生成
    默认基于中译英、交换、省略中间名、去掉连字符、缩写五种规则生成署名
    '''
    __version__ = 20220221
    
    Rules = [RuleC2e, RuleSwap, RuleMid, RuleHyphen, RuleShort]
    def __init__ (this, name, given=None, Rules=None):
        this.name = name
        this.signs = None
        this.std = None
        
        if given is None: given = []
        if isinstance(given, str): given = [given]
        this.given = [*given]
        
        if Rules is None: Rules = SignMaker.Rules
        this.Rules = Rules
        
        this.stdName()
    
    def stdName (this):
        this.std = makeStd(this.name)
        return this.std
    
    def makeSign (this):
        if this.std is None: return None
        rst = this.signs = {this.std : 'std'}
        rst.update({makeStd(x) : 'given/std' for x in this.given})
        
        for Rule in this.Rules:
            rst = this.signs = Rule()(rst)
        return rst
    
    __call__ = makeSign