import re, sys, os, json
import pandas as pd

import unicodedata

from vUtil.vLang import countChinese, hasChinese

def sInSet (db, values):
    values = [db.stdSqlDataRemain(x) for x in set(values)]
    s = ','.join(values)
    return f'''({s})'''

def removeAccents(s):
    s = unicodedata.normalize('NFKD', s)
    def name (c):
        try: return unicodedata.name(c)
        except: return ''
    return "".join([c for c in s if 'COMBINING' not in name(c)])

def makeStd (name):
    '''
    过滤无效姓名，生成有效姓名
    
    按.、空格、大写分词
    去除,-
    缩写在最后将和倒数第二个词交换
    '''
    if not name: return None
    
    name = removeAccents(name).strip()
    name = name.replace('_', ' ')

    symbols = [
        *',，†‡',
        r'\(', r'\)',
        r'\[No Value\]',
    ]
    name = re.sub('|'.join(symbols), ' ', name)

    name = re.sub(r'\d+', ' ', name)
    name = re.sub(r'\s+', '' if hasChinese(name) else ' ', name)
    cnt = countChinese(name)
    
    if '、' in name: return None
    if 5 <= cnt: return None
    if 5 < len(name.split()): return None
    if cnt and '·' in name: return None
    if cnt and len(name) != cnt: return None
    if 1 < name.count(',') or 1 < name.count('，'): return None
    if cnt: return name
    
    if 5 <= len([1 for x in name if x.isupper()]): name = name.lower()
    name = ' '.join([x.lower() if x.isupper() else x for x in name.split()])
    rst = ''
    start = True
    for x in name:
        if x == '.':
            rst += x + ' '
            start = True
        elif x == ' ':
            rst += x
            start = True
        elif x.isupper():
            if not start: rst += ' '
            rst += x
            start = False
        elif start:
            rst += x.upper()
            start = False
        else: rst += x
    
    
    rst = re.sub(r'\s*-+\s*', '-', rst)
    rst = re.sub(r'^-|-$', '', rst)
    rst = re.sub(r'\s+', ' ', rst).strip()
    rst = [x for x in rst.split() if x != '.']
    if not rst: return None
    if isShort(rst[-1]) and 1 < len(rst):
        for i in range(len(rst) - 1):
            if not isShort(rst[i]):
                rst = [*rst[:i], rst[-1], *rst[i+1:-1], rst[i]]
                break
    return ' '.join(rst)

def makeMatch (name):
    rst = re.sub('\.|·|,', '', name)
    rst = re.sub('-', ' ', rst)
    return re.sub(r'\s+', ' ', rst).strip().lower()

def isShort (name):
    for x in name.split():
        rst = True
        for y in x.split('-'):
            if not(len(y) == 2 and y.endswith('.') or len(y) == 1):
                rst = False
                break
        if rst: return True
    return False