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
    from .cfg import updateGapEnterprise, updateGapKeyword, mysqlDb
else:
    from cfg import updateGapEnterprise, updateGapKeyword, mysqlDb

from vUtil.vTime import getNow
from vMysql import MysqlProxy, stdSqlData as stdData

__version__ = 20210831
__author__ = 'LymphV@163.com'

db = MysqlProxy(db=mysqlDb)

keywordDb = 'landinn'

def stdCol (s):
    '''
    列名插入sql语句格式化
    '''
    return f'`{s}`'


def checkEnterprise (id):
    '''
    检查是否存在更新时间在距今updateGap以内的企业（存在则不需要更新）
    '''
    maxUpdateTime = str(ts(getNow()) - td(f'{updateGapEnterprise}s'))
    rst = db.select('id', f'`{mysqlDb}`.`enterprise`', where=f'id={stdData(id)} and updated_at>{stdData(maxUpdateTime)}')
    return bool(len(rst))

def checkKeyword (keyword):
    '''
    检查是否存在更新时间在距今updateGap以内的关键词（存在则不需要更新）
    '''
    maxUpdateTime = str(ts(getNow()) - td(f'{updateGapKeyword}s'))
    rst = db.select('*', f'`{keywordDb}`.`keyword`', where=f'keyword={stdData(keyword)} and updated_tianyancha>{stdData(maxUpdateTime)}')
    return bool(len(rst))

def insert (table, *args, ignore='', replace=''):
    if replace: ignore = False
    sqlInsert = f'''{'replace' if replace else 'insert'} {'ignore' if ignore else ''} into {table} values %s;'''
    value = '(' + ','.join([stdData(x) for x in args]) + ')'
    db.sql(sqlInsert % value, True)

def insertPart (table, values, ignore='', replace=''):
    if replace: ignore = False
    sqlInsert = f'''{'replace' if replace else 'insert'} {'ignore' if ignore else ''} into {table} %s values %s;'''
    col, value = [*zip(*values.items())]
    col = '(' + ','.join([stdCol(x) for x in col]) + ')'
    value = '(' + ','.join([stdData(x) for x in value]) + ')'
    db.sql(sqlInsert % (col, value), True)
    

def insertMulti (table, values, ignore='', replace=''):
    if len(values) == 0: return
    if replace: ignore = False
    sqlInsert = f'''{'replace' if replace else 'insert'} {'ignore' if ignore else ''} into {table} values %s;'''
    values = ['(' + ','.join([stdData(y) for y in x]) + ')' for x in values]
    values = ','.join(values)
    db.sql(sqlInsert % values, True)

def delete (table, col, eid):
    sqlDelete = f'''delete from {table} where {col}={stdData(eid)};'''
    db.sql(sqlDelete, True)

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
            websiteList, email, establishmentTime, companyOrgType, staffNumRange, 
            nStaff, nTeamMember, nProduct, nTrademark, nPatent, 
            nSoftwareCopyright, nWebsite)
        '''
        now = this.now if this.now else getNow()
        table = f'`{mysqlDb}`.`enterprise`'
        
        id = kw.get('id', None)
        if id is None: return
        
        ### 创建时间（created_at）
        t = db.select('created_at', table, where=f'id={stdData(id)}')
        createdAt = t['created_at'][0] if len(t) else getNow()
        
        #delete (table, 'id', id)
        # cols = ['id', 'regNumber', 'creditCode', 'taxNumber', 'name', 'name_en', 
        #     'alias', 'historyNames', 'historyNameList', 'legalPersonName',
        #     'regCapital', 'industry', 'regLocation', 'businessScope', 'phoneNumber', 
        #     'websiteList', 'email', 'establishmentTime', 'companyOrgType', 'staffNumRange', 
        #     'nStaff', 'nTeamMember', 'nProduct', 'nTrademark', 'nPatent', 
        #     'nSoftwareCopyright', 'nWebsite']
        # args = [kw.get(c, None) for c in cols]

        kw['created_at'] = createdAt
        kw['updated_at'] = now
        insertPart(table, kw, replace=True)

    def insertKeyword (this, keyword):
        '''
        插入关键词
        
        Parameters
        ----------
        keyword : 关键词
        '''
        now = this.now if this.now else getNow()
        table = f'`{keywordDb}`.`keyword`'
        
        ### 创建时间（created_at）
        t = db.select('created_at', table, where=f'keyword={stdData(keyword)}')
        createdAt = t['created_at'][0] if len(t) else getNow()
        
        #delete (table, 'keyword', keyword)
        insertPart(table, {
            'keyword' : keyword,
            'created_at' : createdAt,
            'updated_tianyancha' : now,
        }, replace=True)


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
        db.sql(f'''
            update `{mysqlDb}`.`human` set `name` = {stdData(name)} 
            where (`id` = {stdData(id)});
            ''', True)
    if description is not None:
        db.sql(f'''
            update `{mysqlDb}`.`human` set `description` = {stdData(description)} 
            where (`id` = {stdData(id)});
            ''', True)
    if icon is not None:
        db.sql(f'''
            update `{mysqlDb}`.`human` set `icon` = {stdData(icon)} 
            where (`id` = {stdData(id)});
            ''', True)

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
    websites : (webName, ym, website, liscense, companyName)的列表
    '''
    table = f'`{mysqlDb}`.`website`'
    #delete(table, 'eid', eid)
    insertMulti(table, [
        (eid, *w)
        for w in websites
    ], replace=True)

