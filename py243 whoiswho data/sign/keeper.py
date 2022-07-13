import numpy as np, pandas as pd
import pymysql
from time import sleep

from .utils import makeMatch, makeStd, isShort, sInSet, removeAccents
from .cfg import tableDone, tableRule, tableSign, tableError
from .maker import SignMaker

from vUtil.vLog import vError, frmt
from vUtil.vTqdm import tqdm

class RuleManager:
    '''
    规则表管理
    '''
    
    def __init__ (this, db, table=tableRule, id='id', rule='rule'):
        this.db = db
        this.table = table
        this.rule = rule
        this.id = id
        this.rst = {}
    
    def __updateRules (this, rules):
        db = this.db
        s = '(' + ','.join(db.stdSqlData(x) for x in rules) + ')'
        rst = db.select([this.id, this.rule], this.table, where=f'{db.stdSqlCol(this.rule)} in {s}')
        this.rst.update({rst[this.rule][i] : rst[this.id][i] for i in range(len(rst))})
    
    def addRules (this, rules):
        if not rules: return this
        this.rst.update({x : None for x in rules})
        
        db = this.db
        this.__updateRules(rules)
        
        rules = [x for x, y in this.rst.items() if y is None]
        if not rules: return this
        db.insert(this.table, df=pd.DataFrame({this.rule : rules}), ignore=True)
        this.__updateRules(rules)
        
        return this
    
    def getRuleId (this, rule):
        return this.rst.get(rule, None)
    
    __call__ = getRuleId

def errorName (db, id, maker, tableError=tableError):
    if maker.std is not None: return True
    if id is not None: db.insert(tableError, id=id, name=maker.name, replace=True)
    else: vError(f'error name({maker.name})')
    return False

class SignKeeper:
    '''
    署名存储
    '''
    __version__ = 20220221
    cols = ['name', 'sign', 'match', 'rule']
    doneCols = ['name', 'version']
    def __init__ (this, db, *makers, ruleManager=None, tableSign=tableSign, tableDone=tableDone):
        this.makers = makers
        this.db = db
        this.ruleManager = ruleManager or RuleManager(db)
        this.tableSign = tableSign
        this.tableDone = tableDone
    
    def check (this, *names):
        if not names: return {}
        db, tableDone = this.db, this.tableDone
        names = set(names)

        # tableTmp = 'tmp'
        # sCreate = f'''
        # create temporary table {tableTmp}
        # (name char(255), primary key (name))
        # DEFAULT CHARSET=utf8mb4;
        # '''

        # dfInsert = pd.DataFrame({'name' : [*names]})
        
        # sSelect = f'''
        # select t.name, a.version
        # from {tableTmp} as t join {tableDone} as a
        # on t.name = a.name;
        # '''

        ### 数据库ai_ci无视重音和大小写，所以需要保存query字段
        # i = 1
        # while 1:
        #     try:
        #         db(sCreate, ifCommit=True, ifRetry=False)
        #         db.insert(tableTmp, df=dfInsert, ifCommit=True, ifRetry=False)
        #         lastVersion = db(sSelect, ifCommit=True, ifRetry=False)
        #         break
        #     except pymysql.err.Error as e:
        #         code = e.args[0]
        #         if code in db.codeErr or db.maxErr <= i: raise e
        #         sleep(1)
        #         i += 1
        # rst = {name : None for name in names}
        # rst.update({name : version for _, (name, version) in lastVersion.iterrows()})
        
        sNames = sInSet(db, names)
        lastVersion = db.select('name, version', tableDone, where=f'name in {sNames}')

        ### 数据库无视大小写和变音，但python区分
        rst = {removeAccents(name).lower() : None for name in names}
        rst.update({removeAccents(name).lower() : version for _, (name, version) in lastVersion.iterrows()})
        return rst

    def keepSign (this):
        if not this.makers: return 0
        makers, db, ruleManager = this.makers, this.db, this.ruleManager
        tableDone, tableSign = this.tableDone, this.tableSign
        
        lastVersion = this.check(*[maker.name for maker in makers])

        outofdate = []
        rst = pd.DataFrame(columns=this.cols)
        done = pd.DataFrame(columns=this.doneCols)
        makers = [
            maker
            for maker in makers 
            if lastVersion[removeAccents(maker.name).lower()] is None 
            or lastVersion[removeAccents(maker.name).lower()] < maker.__version__
        ]

        if not makers: return 0

        with tqdm(makers, leave=False) as tqm:
            frmt('make signs', tqdm=tqm)
            for maker in tqm:
                version = maker.__version__
                name = maker.name
                frmt(f'make signs({name})', tqdm=tqm)

                lv = lastVersion[removeAccents(name).lower()]
                if lv is not None and version <= lv: continue
                if lv is not None and lv < version: outofdate.append(name)
                maker()
                ruleManager.addRules(maker.signs.values())
                for sign, rule in maker.signs.items():
                    rst.loc[len(rst)] = [name, sign, makeMatch(sign), ruleManager(rule)]
                done.loc[len(done)] = [name, version]
        

        if outofdate:
            '''
            删除过期署名（待完成）
            '''
        
        db.insert(tableSign, df=rst, replace=True)
        db.insert(tableDone, df=done, replace=True)
        return len(rst)
    
    __call__ = keepSign