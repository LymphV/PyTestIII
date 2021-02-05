

import pandas as pd

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


def __std (s):
    return repr(s) if s else 'null'

def checkScholar (id):
    rst = select('id', '`AminerClimbed`.`scholar`', where=f'id={__std(id)}')
    return bool(len(rst))

def checkDoneName (name):
    rst = select('name', '`AminerClimbed`.`done_name`', where=f'name={__std(name)}')
    return bool(len(rst))

def insert (table, *args):
    sqlInsert = f'''insert into {table} values %s;'''
    value = '(' + ','.join([__std(x) for x in args]) + ')'
    sql(sqlInsert % value)

def insertMulti (table, values, ignore=''):
    if len(values) == 0: return
    sqlInsert = f'''insert {ignore} into {table} values %s;'''
    values = ['(' + ','.join([__std(y) for y in x]) + ')' for x in values]
    values = ','.join(values)
    sql(sqlInsert % values)

def insertScholar (*args):
    '''
    (id, name, pinyin, phone, title, department, fax, email, address, experience, education, brief)
    '''
    insert('`AminerClimbed`.`scholar`', *args)

def insertDoneName (name):
    insert('`AminerClimbed`.`done_name`', name)


def insertWebpages (id, webpages):
    insertMulti('`AminerClimbed`.`webpage`', [
        (id, w) for w in webpages
    ])

def insertPortrait (id, portrait):
    insert('`AminerClimbed`.`portrait`', id, portrait)

def insertAwards (id, awards):
    insertMulti('`AminerClimbed`.`award`', [
        (id, a) for a in awards
    ])

def insertTalentPools (id, talentPools):
    insertMulti('`AminerClimbed`.`talent_pool`', [
        (id, t) for t in talentPools
    ])

def insertPapers (papers):
    '''
    (id, title, authors, venue, cited)
    '''
    insertMulti('`AminerClimbed`.`paper`', [
        (p['id'], p['title'], p['authors'], p['venue'], p['cited'])
        for p in papers
    ], ignore='ignore')

def insertPublish (id, papers):
    insertMulti('`AminerClimbed`.`publish`', [
        (id, p['id']) for p in papers
    ], ignore='ignore')








