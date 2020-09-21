'''

wospidey
========
提供：
    1.以wos核心合集为数据库，按指定时间跨度的关键词检索
    2.以日期降序、被引频次降序、相关性等排序方式排序检索结果
    3.从检索结果中抽取文章的标题、作者、通讯作者、电子邮箱等字段
    
'''
from time import time

if '.' in __name__:
    from .cfg import home
    from .driverOps import getDriver, newLabel, switchLabel, waitTillOpen
    from .searcher import selectDatabase, selectSpan, selectSearchField, search, ifSearchFailed
    from .listExtracter import getIds, sortResults, getNumOfRst, getLnks, MAX_DOC
    from .paperExtracter import extractValues
else:
    from cfg import home
    from driverOps import getDriver, newLabel, switchLabel, waitTillOpen
    from searcher import selectDatabase, selectSpan, selectSearchField, search, ifSearchFailed
    from listExtracter import getIds, sortResults, getNumOfRst, getLnks, MAX_DOC
    from paperExtracter import extractValues

class Wospidey:
    '''
    wospidey
    ========
    提供：
        1.以wos核心合集为数据库，按指定时间跨度的关键词检索
        2.以日期降序、被引频次降序、相关性等排序方式排序检索结果
        3.从检索结果中抽取文章的标题、作者、通讯作者、电子邮箱等字段
    '''
    
    __version__ = 20200921
    __author__ = 'LymphV@163.com'
    
    def __init__ (this, ifHeadless = True, home = home):
        '''
        wospidey初始化
        
        Parameters
        ----------
        ifHeadless : 是否为无头浏览器，默认为True，使用有头浏览器便于调试
        home : wos搜索页，默认为cfg.py中的home
        '''
        this.home = home
        this.driver = getDriver(ifHeadless)
        print('INFO : web driver created')
    
    def __waitTillOpen (this):
        '''
        打开paper页时等待页面加载
        如果长时间打不开则视为被反爬系统禁止访问
        
        Raise
        -----
        Exception : paper页打不开报错
        '''
        for i in range(6):
            try:
                waitTillOpen(this.driver, 10)
                if i: print('INFO : open succeed, tried %dth' % (i + 1), ' ' * 20)
                break
            except TimeoutException as e:
                print ('ERROR : failed to open the page of paper, tried %dth' % (i + 1), end = '\r')
        else:
            print()
            raise Exception('maybe banned by wos, please check')
    
    def crawl (this, keyWord, nReq = MAX_DOC, sortReq = '', fieldReq = '', timeSpan = None):
        '''
        一个生成器，用于采集数据
        以wos核心合集为数据库，按指定时间跨度的关键词检索
        以日期降序、被引频次降序、相关性等排序方式排序检索结果
        从检索结果中抽取文章的标题、作者、通讯作者、电子邮箱等字段
        
        Parameters
        ----------
        keyWord : 关键词
        nReq : 需要采集的条数，默认为全采
        sortReq : 检索结果排序代码，见sortId.py
        timeSpan : 检索的时间跨度
        
        Returns
        -------
        crawl : 一个生成器，生成获取的paper各字段
        '''
        
        if nReq is None or nReq < 0: nReq = MAX_DOC
        
        driver = this.driver
        driver.get(this.home)
        print('INFO : home page opened')
        
        selectDatabase(driver)
        print('INFO : database selected')
        
        selectSpan(driver, timeSpan)
        print('INFO : time span selected')

        selectSearchField(driver, fieldReq)
        print('INFO : search field selected')
        
        
        search(driver, keyWord)
        
        msg = ifSearchFailed(driver)
        assert not msg, 'search failed : "%s"' % msg
        
        print('INFO : search succeed')

        sid, qid = getIds(driver)
        sortResults(driver, sid, qid, sortReq)
        print('INFO : sort succeed')
        
        nRst = getNumOfRst(driver)
        
        if MAX_DOC < nRst:
            print('WARNING : too much results, please consider shortening time span')
        
        switchLabel(driver, -1)
        
        print('INFO : start to extract data')
        i = 0
        maxI = min(nReq, nRst, MAX_DOC)
        
        tStart = time()
        ts = tc = 0
        for lnk in getLnks(driver, nReq, nRst):
            i += 1
            sTimeCost = ', %.2fs last page'
            print('INFO : extracting %d/%d%s' % (i, maxI,
                    '' if i == 1 else sTimeCost % tc), end = '\r')
            
            ts = time()
            newLabel(driver, lnk)
            switchLabel(driver, -1)
            
            this.__waitTillOpen()
            
            rst = extractValues(driver)
            driver.close()
            switchLabel(driver,-1)
            tc = time() - ts
            
            yield rst
        tCost = time() - tStart
        print('\nINFO : extracting done, %.2fs/paper' % (tCost / maxI))
    
    def close (this):
        '''
        关闭wospidey，退出浏览器
        '''
        this.driver.quit()
        del this.driver
        print('INFO : web driver closed')
        
        













