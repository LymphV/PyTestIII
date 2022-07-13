'''

天眼查数据入库

-------------------

checkEnterprise : 检查是否存在更新时间在距今updateGap以内的企业（存在则不需要更新）
checkKeyword : 检查是否存在更新时间在距今updateGap以内的关键词（存在则不需要更新）
MysqlUpdateTimeInserter : 插入企业和关键词（为方便传参更新时间）
insertStaffs : 插入主要人员
insertHuman : 插入人
insertTeamMembers : 插入核心团队
insertProducts : 插入企业业务
insertTrademarks : 插入商标
insertPatents : 插入专利
insertSoftwareCopyrights : 插入软件著作权
insertWebsites : 插入网站备案

'''

import pandas as pd
from pandas._libs.tslibs.timedeltas import Timedelta as td
from pandas import Timestamp as ts


if '.' in __name__:
    from .cfg import updateGap, mysqlDb
else:
    from cfg import updateGap, mysqlDb

from vUtil.vTime import getNow

cursor = []
def addCursor (cr):
    cursor.append(cr)


def sql(s):
    cursor[-1].execute(s)
    rst = cursor[-1].fetchall()
    
    rst = pd.DataFrame(rst, columns=[*zip(*cursor[-1].description)][0] if cursor[-1].description else [])
    return rst
    
def select (items, table, *args, **kwargs):
    def deal (s):
        s = str(s).strip()
        return f'`{s}`' if s.isalnum() else s
    
    
    if type(items) is str:
        items = items.split(',')
    item = ','.join([deal(x) for x in items])
        
    if args:
        r = range(*args)
        start, stop = r.start, r.stop
        limit = f'limit {start}, {stop - start}'
    else: limit = ''
    
    s = f'select {item} from {deal(table)} {" ".join([f"{x} {kwargs[x]}" for x in kwargs if kwargs[x].strip()])} {limit}'
    
    rst = sql(s)
    rst.columns.name = table
    return rst


def stdData (s):
    '''
    变量插入sql语句格式化
    '''
    if s is None or s == '': return 'null'
    if type(s) in [list, dict, set]: s = str(s)
    return repr(s)

def checkEnterprise (id):
    '''
    检查是否存在更新时间在距今updateGap以内的企业（存在则不需要更新）
    '''
    maxUpdateTime = str(ts(getNow()) - td(f'{updateGap}s'))
    rst = select('id', f'`{mysqlDb}`.`enterprise`', where=f'id={stdData(id)} and updated_at>{stdData(maxUpdateTime)}')
    return bool(len(rst))

def checkKeyword (keyword):
    '''
    检查是否存在更新时间在距今updateGap以内的关键词（存在则不需要更新）
    '''
    maxUpdateTime = str(ts(getNow()) - td(f'{updateGap}s'))
    rst = select('*', f'`{mysqlDb}`.`keyword`', where=f'keyword={stdData(keyword)} and updated_at>{stdData(maxUpdateTime)}')
    return bool(len(rst))

def insert (table, *args, ignore='', replace=''):
    if replace: ignore = False
    sqlInsert = f'''{'replace' if replace else 'insert'} {'ignore' if ignore else ''} into {table} values %s;'''
    value = '(' + ','.join([stdData(x) for x in args]) + ')'
    sql(sqlInsert % value)

def insertMulti (table, values, ignore='', replace=''):
    if len(values) == 0: return
    if replace: ignore = False
    sqlInsert = f'''{'replace' if replace else 'insert'} {'ignore' if ignore else ''} into {table} values %s;'''
    values = ['(' + ','.join([stdData(y) for y in x]) + ')' for x in values]
    values = ','.join(values)
    sql(sqlInsert % values)

def delete (table, col, eid):
    sqlDelete = f'''delete from {table} where {col}={stdData(eid)};'''
    sql(sqlDelete)

class MysqlUpdateTimeInserter:
    '''
    插入企业和关键词（为方便传参更新时间）
    
    ------
    
    insertEnterprise : 插入企业
    insertKeyword : 插入关键词
    '''
    def __init__ (this, now=None):
        '''
        Parameters
        ----------
        now : 更新时间（updated_at）
        '''
        this.now = now

    def insertEnterprise (this, **kw):
        '''
        插入企业
        
        Parameters
        ----------
        **kw : 映射，包含以下键
            (id, regNumber, creditCode, taxNumber, name, name_en, 
            alias, historyNames, historyNameList, legalPersonName,
            regCapital, industry, regLocation, businessScope, phoneNumber, 
            websiteList, email, establishmentTime, staffNumRange, nStaff,
            nTeamMember, nProduct, nTrademark, nPatent, 
            nSoftwareCopyright, nWebsite)
        '''
        now = this.now if this.now else getNow()
        table = f'`{mysqlDb}`.`enterprise`'
        
        id = kw.get('id', None)
        if id is None: return
        
        ### 创建时间（created_at）
        t = select('created_at', table, where=f'id={stdData(id)}')
        createdAt = t['created_at'][0] if len(t) else getNow()
        
        #delete (table, 'id', id)
        cols = ['id', 'regNumber', 'creditCode', 'taxNumber', 'name', 'name_en', 
            'alias', 'historyNames', 'historyNameList', 'legalPersonName',
            'regCapital', 'industry', 'regLocation', 'businessScope', 'phoneNumber', 
            'websiteList', 'email', 'establishmentTime', 'staffNumRange', 'nStaff',
            'nTeamMember', 'nProduct', 'nTrademark', 'nPatent', 
            'nSoftwareCopyright', 'nWebsite']
        args = [kw.get(c, None) for c in cols]
        insert(table, *args, createdAt, now, replace=True)

    def insertKeyword (this, keyword):
        '''
        插入关键词
        
        Parameters
        ----------
        keyword : 关键词
        '''
        now = this.now if this.now else getNow()
        table = f'`{mysqlDb}`.`keyword`'
        
        ### 创建时间（created_at）
        t = select('created_at', table, where=f'keyword={stdData(keyword)}')
        createdAt = t['created_at'][0] if len(t) else getNow()
        
        #delete (table, 'keyword', keyword)
        insert(table, keyword, createdAt, now, replace=True)


def insertStaffs (eid, staffs):
    '''
    插入主要人员
    
    Parameters
    ----------
    staffs : (sid, name, type, typeJoin)的列表
    '''
    table = f'`{mysqlDb}`.`staff`'
    delete(table, 'eid', eid)
    insertMulti(table, [
        (eid, *staff) for staff in staffs
    ], ignore='ignore')

def insertHuman (**human):
    '''
    插入人
    
    Parameters
    ----------
    **human : 映射，包含以下键(id, name, description, icon)
    '''
    id = human.get('id', None)
    name = human.get('name', None)
    description = human.get('description', None)
    icon = human.get('icon', None)
    
    if id is None: return
    
    insert(f'`{mysqlDb}`.`human`', id, None, None, None, ignore=True)
    if name is not None:
        sql(f'''
            update `{mysqlDb}`.`human` set `name` = {stdData(name)} 
            where (`id` = {stdData(id)});
            ''')
    if description is not None:
        sql(f'''
            update `{mysqlDb}`.`human` set `description` = {stdData(description)} 
            where (`id` = {stdData(id)});
            ''')
    if icon is not None:
        sql(f'''
            update `{mysqlDb}`.`human` set `icon` = {stdData(icon)} 
            where (`id` = {stdData(id)});
            ''')

def insertTeamMembers (eid, teamMembers):
    '''
    插入核心团队
    
    Parameters
    ----------
    teamMembers : (hid, name, isDimision, title, icon, description)的列表
    '''
    table = f'`{mysqlDb}`.`teamMember`'
    delete(table, 'eid', eid)
    insertMulti(table, [
        (eid, *tm) for tm in teamMembers
    ], ignore='ignore')

def insertProducts (eid, products):
    '''
    插入企业业务
    
    Parameters
    ----------
    products : (hangye, yewu, product, logo, setupTime)的列表
    '''
    table = f'`{mysqlDb}`.`product`'
    #delete(table, 'eid', eid)
    insertMulti(table, [
        (eid, *p) for p in products
    ], replace=True)

def insertTrademarks (eid, trademarks):
    '''
    插入商标
    
    Parameters
    ----------
    trademarks : (id, intCls, title, regNo, applicantCn, pic)的列表
    '''
    table = f'`{mysqlDb}`.`trademark`'
    #delete(table, 'eid', eid)
    insertMulti(table, [
        (t[0], eid, *t[1:])
        for t in trademarks
    ], replace=True)

def insertPatents (eid, patents):
    '''
    插入专利
    
    Parameters
    ----------
    patents : (id, uuid, title, appNumber, pubNumber, patentNumber, 
        allCatNumber, lawStatus, abstract, 
        applicationTime, pubDate, applicationPublishTime, 
        inventor, applicationNameList, applicationName, agent,
        agency, address, patentType)的列表
    '''
    table = f'`{mysqlDb}`.`patent`'
    #delete(table, 'eid', eid)
    insertMulti(table, [
        (p[0], eid, *p[1:]) for p in patents
    ], replace=True)

def insertSoftwareCopyrights (eid, softwareCopyrights):
    '''
    插入软件著作权
    
    Parameters
    ----------
    softwareCopyrights : (id, regNum, version, fullName, simpleName, 
        regTime, publishTime, eventTime, authorNationality)的列表
    '''
    table = f'`{mysqlDb}`.`softwareCopyright`'
    #delete(table, 'eid', eid)
    insertMulti(table, [
        (sc[0], eid, *sc[1:])
        for sc in softwareCopyrights
    ], replace=True)

def insertWebsites (eid, websites):
    '''
    插入网站备案
    
    Parameters
    ----------
    softwareCopyrights : (webName, ym, website, liscense, companyName)的列表
    '''
    table = f'`{mysqlDb}`.`website`'
    #delete(table, 'eid', eid)
    insertMulti(table, [
        (eid, *w)
        for w in websites
    ], replace=True)

