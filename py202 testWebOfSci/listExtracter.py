'''

在search result页的一些操作
webdriver当前标签页为search result页

------------------

getIds : 获取sid和qid
sortResults : 按需求对检索结果排序
getNumOfRst : 获取检索结果的数量
getLnks : 一个生成器，从search result页获取paper链接

'''

import re

from sortId import str2SortId, SortId

###wos检索结果中可显示和读取的最大数量
MAX_DOC = 100000

def getIds (dv):
    '''
    获取sid和qid
    sid决定用户session，qid决定检索编号，二者共同决定检索结果
    
    Parameters
    ----------
    dv : 当前handle是search result页的webdriver
    
    Returns
    -------
    getIds : 返回id对(sid, qid)
    '''
    
    sid = dv.execute_script('return SID')
    qid = dv.execute_script('return qid.value')
    return sid, qid



def __getSortJs (sid, qid, sortId):
    '''
    获取结果排序js
    
    Parameters
    ----------
    sid : sid
    qid : qid
    sortId : sort id
    '''
    
    sortJs = '''
        trackSnowplowEventSE('sort-sort-method-top-click', '%s');
        handle_sort(undefined, 1, 
        'http://apps.webofknowledge.com/summary.do?product=WOS&parentProduct=WOS&search_mode=GeneralSearch&qid=%s&SID=%s&&page=',
        '1', 'sort', '%s' , '1');
    '''
    return sortJs % (sortId, qid, sid, sortId)



def sortResults (dv, sid, qid, sortReq = ''):
    '''
    按需求对检索结果排序
    
    Parameters
    ----------
    dv : 当前handle是search result页的webdriver
    sid : sid
    qid : qid
    sortReq : 排序需求，默认或无效需求视为“日期降序”
    '''
    
    if type(sortReq) is not str: sortReq = ''
    sortId = str2SortId.get (sortReq.upper(), SortId.PYD)
    dv.execute_script(__getSortJs(sid,qid,sortId))


def getNumOfRst (dv):
    '''
    获取检索结果的数量
    
    Parameters
    ----------
    dv : 当前handle是search result页的webdriver
    
    Returns
    -------
    getNumOfRst : 检索结果的数量
    '''
    
    nRstPath = '//h3[@class="title4"]/*'
    return int(dv.find_element_by_xpath(nRstPath).text.replace(',',''))

def __getPattern (lnk):
    '''
    获取paper链接的pattern
    将doc编号和page编号替换为%d
    '''
    
    rst = lnk.replace('%', '%%')
    rst = re.sub(r'page=\d+', 'page=%d', rst)
    return re.sub(r'doc=\d+', 'doc=%d', rst)

def __getLnk (doc, pat):
    '''
    根据pattern获取paper链接
    目前，page编号事实上并没有什么卵用
    '''
    return pat % ((doc - 1) // 10 + 1, doc)

def getLnks(dv, nReq, nRst = None):
    '''
    一个生成器，从search result页获取paper链接
    
    Parameters
    ----------
    dv : 当前handle是search result页的webdriver
    nReq : 采集paper数量的需求
    nRst : 检索结果的数量，靠getNumOfRst获取
    
    Returns
    -------
    getLnks : 一个生成器，生成获取的paper链接
    '''
    
    if nRst is None: nRst = getNumOfRst(dv)
    
    ###paper链接xpath
    lnkPath = '//a[@class="smallV110 snowplow-full-record"]'
    lnk = dv.find_element_by_xpath(lnkPath)
    
    pat = __getPattern(lnk.get_attribute('href'))
    
    for doc in range(1, 1 + min(nReq, nRst, MAX_DOC)):
        yield __getLnk(doc, pat)
    

















