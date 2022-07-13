
from .keeper import RuleManager, errorName, SignKeeper
from .maker import SignMaker
from .cfg import tableDone, tableRule, tableSign, tableError, schema
from .utils import sInSet, removeAccents

from vMysql import MysqlProxy
from vUtil.vTqdm import tqdm
from vUtil.vLog import frmt

def makeSign (db, name, ruleManager):
    maker = SignMaker(name)
    if errorName(db, None, maker): 
        SignKeeper(db, maker, ruleManager=ruleManager)()
        return True
    return False

def makeSigns (db, *names, single=True):
    if not names: return []
    ruleManager = RuleManager(db)
    if single and len(names) == 1:
        return makeSign(db, names[0], ruleManager)

    rst = {}
    makers = []
    for name in set(names):
        maker = SignMaker(name)
        if errorName(db, None, maker):
            makers.append(maker)
            rst[name] = True
        else: rst[name] = False
    SignKeeper(db, *makers, ruleManager=ruleManager)()
    return rst
    # return [rst[name] for name in names]   

def baseGetCandidate (f):
    def _baseGetCandidate (db, *names, banShort=False, single=True):
        if not names: return {}
        if single and len(names) == 1:
            if makeSigns(db, names[0]):
                s = f(db, sInSet(db, names), banShort=banShort)
                return [*db(s, ifCommit=True)['candidate']]
            else:
                return [*names]
        
        valid = makeSigns (db, *names, single=False)
        validNames = {name for name in valid if valid[name]}
        rst = {removeAccents(name).lower() : [] for name in validNames}
        if validNames:
            s = f(db, sInSet(db, validNames), banShort=banShort)
            cans = db(s, ifCommit=True)
            for _, (name, candidate) in cans.iterrows():
                rst[removeAccents(name).lower()].append(candidate)
        return {name : rst[removeAccents(name).lower()] if valid[name] else [name] for name in valid}

    return _baseGetCandidate

@baseGetCandidate
def getCandidate (db, sNames, banShort):
    if banShort:
        short1 = f'''and a.rule not in (select id from {tableRule} where rule like '%short%')'''
        short2 = f'''and b.rule not in (select id from {tableRule} where rule like '%short%')'''
    else: short1 = short2 = ''

    s = f'''
    select a.name, b.name as candidate
    from {tableSign} as a
    join {tableSign} as b
    join {tableRule} as c
    on c.rule = 'std' and a.match = b.match and a.name in {sNames} and b.rule = c.id
    {short1}
    union
    select a.name, b.name as candidate
    from {tableSign} as a
    join {tableSign} as b
    join {tableRule} as c
    on c.rule = 'std' and a.match = b.match and a.name in {sNames} and a.rule = c.id
    {short2};
    '''
    return s

@baseGetCandidate
def getFullCandidate (db, sNames, banShort):
    if banShort:
        short1 = f'''and b.rule not in (select id from {tableRule} where rule like '%short%')'''
        short2 = f'''and d.rule not in (select id from {tableRule} where rule like '%short%')'''
    else: short1 = short2 = ''

    s = f'''
    select distinct a.name, e.name as candidate
    from {tableSign} as a
    join {tableSign} as b
    join {tableRule} as c
    join {tableSign} as d
    join {tableSign} as e
    join {tableRule} as f
    on c.rule = 'std' and a.match = b.match and a.name in {sNames} and a.rule = c.id
    and f.rule = 'std' and d.match = e.match and d.name = b.name and e.rule = f.id
    {short1}
    {short2}
    ;
    '''
    return s

# def baseGetCandidate (f):
#     def _baseGetCandidate (db, *names, banShort=False, single=True):
#         if not names: return {}        
#         if single and len(names) == 1:
#             if makeSigns(db, names[0]):
#                 s = f(db, sInSet(db, names), banShort=banShort)
#                 return [*db(s, ifCommit=True)['candidate']]
#             else:
#                 return [*names]

#         valid = makeSigns (db, *names, single=False)

#         validNames = {name for name in valid if valid[name]}
#         rst = {name.lower() : [] for name in validNames}
#         if validNames:
#             s = f(db, sInSet(db, validNames), banShort=banShort)
#             cans = db(s, ifCommit=True)
#             for _, (name, candidate) in cans.iterrows():
#                 rst[name.lower()].append(candidate)
#         return {name : rst[name.lower()] if valid[name] else [name] for name in valid}

#     return _baseGetCandidate

    
# @baseGetCandidate
# def getCandidate (db, sNames, banShort):
#     if banShort:
#         short1 = f'''and a.rule not in (select id from {tableRule} where rule like '%short%')'''
#         short2 = f'''and b.rule not in (select id from {tableRule} where rule like '%short%')'''
#     else: short1 = short2 = ''

#     s = f'''
#     select a.name, b.name as candidate
#     from {tableSign} as a
#     join {tableSign} as b
#     join {tableRule} as c
#     on c.rule = 'std' and a.match = b.match and a.name in {sNames} and b.rule = c.id
#     {short1}
#     union
#     select a.name, b.name as candidate
#     from {tableSign} as a
#     join {tableSign} as b
#     join {tableRule} as c
#     on c.rule = 'std' and a.match = b.match and a.name in {sNames} and a.rule = c.id
#     {short2};
#     '''
#     return s

# @baseGetCandidate
# def getFullCandidate (db, sNames, banShort):
#     if banShort:
#         short1 = f'''and b.rule not in (select id from {tableRule} where rule like '%short%')'''
#         short2 = f'''and d.rule not in (select id from {tableRule} where rule like '%short%')'''
#     else: short1 = short2 = ''

#     s = f'''
#     select distinct a.name, e.name as candidate
#     from {tableSign} as a
#     join {tableSign} as b
#     join {tableRule} as c
#     join {tableSign} as d
#     join {tableSign} as e
#     join {tableRule} as f
#     on c.rule = 'std' and a.match = b.match and a.name in {sNames} and a.rule = c.id
#     and f.rule = 'std' and d.match = e.match and d.name = b.name and e.rule = f.id
#     {short1}
#     {short2}
#     ;
#     '''
#     return s