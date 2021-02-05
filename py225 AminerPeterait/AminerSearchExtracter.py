'''

从检索列表页抽取学者id
webdriver当前标签页为scholar页

-------------------

searchName : 按姓名检索
getScholarPage : 按学者id打开学者页面
getScholarIds : 抽取学者id
'''

from urllib.request import quote


if '.' in __name__:
    from .driverOps import waitTillOpen, waitTillLoaded
    from .utils import stdAminerId, rmUnseen
    from .driverUtils import getTextByXpath, getAttributeByXpath, getTextById, getTextsByXpath
    from .cfg import waitUnit, waitLoading, home
else:
    from driverOps import waitTillOpen, waitTillLoaded
    from utils import stdAminerId, rmUnseen
    from driverUtils import getTextByXpath, getAttributeByXpath, getTextById, getTextsByXpath
    from cfg import waitUnit, waitLoading, home

def searchName (dv, name):
    '''
    按姓名检索
    
    Returns
    -------
    True : 学者列表加载成功
    False : 学者列表加载失败
    
    '''
    pathLoading = '//span[contains(@class,"ant-spin")]'
    dv.get(f'{home}eb/search?key={quote(name)}')
    ###因为网页是先打开，然后异步加载学者列表，所以网页打开后依然需要等待加载完成
    return waitTillLoaded(dv, waitLoading, value=pathLoading, waitUnit=waitUnit)

def getScholarPage (dv, sid):
    '''
    按学者id打开学者页面
    '''
    dv.get(f'https://top3-talent.com/market/eb/profile/{sid}')


def getScholarIds (dv, name):
    '''
    抽取学者id
    因为Aminer检索没有人名全匹配功能，可能检索到其他相关学者，所以需要再次确认
    返回None为加载失败，需要重新打开页面进行加载
    '''
    path = '//*[contains(@id,"pid_")]'
    pathName = './/strong//span[1]'
    pathNextPage = '//li[contains(@class,"next")]'
    pathLoading = '//span[contains(@class,"ant-spin")]'
    
    rst = []
    
    while 1:
        rst += [
            stdAminerId(x.get_attribute('id')) 
            for x in dv.find_elements_by_xpath(path) 
            if x.find_elements_by_xpath(pathName) 
            and x.find_elements_by_xpath(pathName)[0].text == name
        ]
        
        nextPage = dv.find_elements_by_xpath(pathNextPage)
        if not nextPage or nextPage[0].get_attribute('aria-disabled') != 'false':
            break
        dv.execute_script('arguments[0].click();', nextPage[0])
        
        ###加载失败，需要重新打开列表进行加载
        if not waitTillLoaded(dv, waitLoading, value=pathLoading, waitUnit=waitUnit): return None
    
    return rst