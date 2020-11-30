'''

有道翻译同义词
youdaoSynonym

==============

>>>yd = YoudaoSynonym() ###打开浏览器，打开有道翻译网页
>>>yd.getSynonyms('光学计算') ###生成同义词集
{'Optical computing', 'optical calculation', 'optical computing'}
>>>yd.close() ###关闭浏览器
'''
import re
from time import sleep
from selenium.common.exceptions import TimeoutException

if '.' in __name__:
    from .driverOps import getDriver, waitTillOpen 
    from .cfg import home
else:
    from driverOps import getDriver, waitTillOpen
    from cfg import home



class YoudaoFilter:
    '''
    同义词过滤器
    '''
    ###词性表
    __cixings = ['n', 'pron', 'prep', 'adj', 'adv', 'v', 'num',
              'art', 'conj', 'int', 'abbr']

    ###停用词表
    __stopWords = {'the', 'a', 'an',}
    
    def filterLower (s : str) -> set:
        '''
        大写转小写
        '''
        return {s.lower()}

    def filterTerm (s : str) -> set:
        '''
        去除中括号的术语标志
        '''
        s = re.sub(r'\[.+?\]', ' ', s)
        s = re.sub(r'\[.*?$', '', s)
        s = re.sub(r'^.*?]', '', s)
        return {s}

    def filterBracket (s : str) -> set:
        '''
        去除小括号
        '''
        s = re.sub(r'\(.+?\)', ' ', s)
        s = re.sub(r'（.+?）', ' ', s)
        return {s}

    def filterCixing (s : str) -> set:
        '''
        去除词性标志
        '''
        s = re.sub('|'.join([f'({x}\.)' for x in YoudaoFilter.__cixings]), ' ', s)
        s = re.sub('\.\s*$', '', s)
        return {s}

    def filterComma (s : str) -> set:
        '''
        去除逗号
        '''
        return {s.replace(',', ' ')}

    def filterSemicolon (s : str) -> set:
        '''
        拆分分号
        '''
        return set(s.replace(';','\n').replace('；','\n').split('\n'))

    def filterHyphen (s : str) -> set:
        '''
        生成无连字符词
        '''
        return {s, s.replace('-', ' ')}

    def filterStopWords (s : str) -> set:
        '''
        去除停用词
        '''
        return {' '.join([x for x in s.split() if x and x not in YoudaoFilter.__stopWords])}

    def filterStrip (s : str) -> set:
        '''
        去除空串
        '''
        s = s.strip()
        return {s} if s else set()
    
    filters = [filterLower, filterTerm, filterBracket, filterCixing, filterComma, ###去除一些东西（整体上）
                 filterHyphen, filterSemicolon,###扩展一些东西
                 filterStopWords,###去除一些词（分词后）
                 filterStrip] ###去重去空
    
    def filter (ss : set, filters) -> set:
        '''
        过滤器
        按过滤器顺序处理字符串集合
        '''
        for f in filters:
            rst = set()
            for s in ss:
                rst |= f(s)
            ss = rst
        return ss


class YoudaoSynonym:
    '''
    有道翻译同义词
    YoudaoSynonym

    ==============

    >>>yd = YoudaoSynonym() ###打开浏览器，打开有道翻译网页
    >>>yd.getSynonyms('光学计算') ###生成同义词集
    {'Optical computing', 'optical calculation', 'optical computing'}
    >>>yd.close() ###关闭浏览器，必须
    '''
    
    __version__ = 20201130
    __author__ = 'LymphV@163.com'
    
    __filters = YoudaoFilter.filters

    def __init__ (this, page = home, ifHeadless = True):
        '''
        YoudaoSynonym初始化
        
        Parameters
        ----------
        page : 有道翻译网址，默认为cfg.py中的home
        '''
        this.__dv = None
        this.__ifHeadless = ifHeadless
        this.start(page)
    
    
    def __iknow (this):
        pathClose = '//*[@class="guide-close"]/../../../*[contains(@style,"block")]//*[@class="guide-close"]'
        pathIKnow = '//a[@class="i-know"]/../../div[contains(@style,"block")]//a[@class="i-know"]'
        close = this.__dv.find_elements_by_xpath(pathClose)
        if close: close[0].click()
        iknow = this.__dv.find_elements_by_xpath(pathIKnow)
        if iknow: iknow[0].click()
    
    def __getMode (this):
        pathSelect = '//*[@class="select clear"]/li[contains(@class,"selected")]'
        dv = this.__dv
        return dv.find_element_by_xpath(pathSelect).get_attribute('data-value')
    
    def __ch2en (this):
        pathLang = '//*[@class="select-text"]'
        pathCh2En = '//*[@data-value="zh-CHS2en"]/../../*[contains(@style,"block")]/*[@data-value="zh-CHS2en"]/a'
        pathWait = '//*[@data-value="zh-CHS2en"]/../../*[contains(@style,"none")]/*[@data-value="zh-CHS2en"]'
        
        if this.__getMode() == 'zh-CHS2en': return
        dv = this.__dv
        waitTillOpen(dv, 10, value=pathLang)
        dv.find_element_by_xpath(pathLang).click()
        waitTillOpen(dv, 10, value=pathCh2En)
        dv.find_element_by_xpath(pathCh2En).click()
        waitTillOpen(dv, 10, value=pathWait)
        
    def __auto (this):
        pathLang = '//*[@class="select-text"]'
        pathAuto = '//*[@data-value="AUTO"]/../../*[contains(@style,"block")]/*[@data-value="AUTO"]/a'
        pathWait = '//*[@data-value="AUTO"]/../../*[contains(@style,"none")]/*[@data-value="AUTO"]'
        
        if this.__getMode() == 'AUTO': return
        dv = this.__dv
        waitTillOpen(dv, 10, value=pathLang)
        dv.find_element_by_xpath(pathLang).click()
        waitTillOpen(dv, 10, value=pathAuto)
        dv.find_element_by_xpath(pathAuto).click()
        waitTillOpen(dv, 10, value=pathWait)
    
    def start (this, page = home):
        '''
        打开有道翻译网址
        
        Parameters
        ----------
        page : 有道翻译网址，默认为cfg.py中的home
        '''
        if not page: return
        if not this.__dv:
            this.__dv = getDriver(this.__ifHeadless)
        try:
            this.__dv.get(page)
            this.__iknow()
            #this.__ch2en()
        except BaseException as e:
            this.close()
            raise e
        
    
    def __getSynonyms (this, s : str, mode):
        '''
        使用有道翻译获得同义词集
        '''
        dv = this.__dv
        #dv.refresh()
        pathInput = '//textarea[@class="input__original__area"]'
        pathAnswer = '//div[@class="input__target__text"]/p/span'
        pathSuggestWait = '//*[@class="suggest__title"]/../../*[contains(@style,"block")]'
        pathSuggest = '//*[@class="suggest__title"]/../ul/*'
        pathRelative = '//div[@class="dict__relative"]/*'
        pathTrans = '//a[@id="transMachine"]'
        
        ###翻译语言
        if mode == 'ch2en': this.__ch2en()
        else: this.__auto()
        
        ###输入
        waitTillOpen(dv, 10, value=pathInput)
        ipts = dv.find_elements_by_xpath(pathInput)
        
        this.__iknow()
        
        ipt = ipts[0]
        ipt.clear()
        
        for i in range(10):
            ans = dv.find_elements_by_xpath(pathAnswer)
            if not ans: break
            dv.find_element_by_xpath(pathTrans).click()
            sleep(0.1)
        else: assert 0, 'translate area not cleared'
        
        ipt.send_keys(s)
        
        rst = set()
        
        ###翻译结果
        waitTillOpen(dv, value=pathAnswer)
        ans = dv.find_elements_by_xpath(pathAnswer)
        rst |= {x.text for x in ans}
        if ans:
            ###翻译改进结果
            ans[0].click()
            
            try: 
                waitTillOpen(dv, 10, value=pathSuggestWait)
                sug = dv.find_elements_by_xpath(pathSuggest)
                rst |= {x.text for x in sug}
            except TimeoutException: pass
        
        ###翻译相关结果
        relative = dv.find_elements_by_xpath(pathRelative)
        rst |= {x.text for x in relative}
        this.__auto()
        ipt.clear()
        dv.find_element_by_xpath(pathTrans).click()
        return rst
    
    def __filter (this, ss : set) -> set:
        '''
        过滤器
        过滤掉短语中的标点符号、停用词、词性、术语标志等
        '''
        return YoudaoFilter.filter(ss, YoudaoSynonym.__filters)

    
    def getSynonyms (this, s : str, mode = '') -> set:
        '''
        获取中文短语的英语同义词集合
        
        Parameters
        ----------
        s : 中文短语
        
        Returns
        -------
        getSynonyms : 英文同义词集合
        '''
        return this.__filter(this.__getSynonyms(s, mode.lower()))
    def close (this):
        '''
        关闭浏览器，必须
        '''
        if this.__dv:
            this.__dv.quit()
            this.__dv = None
