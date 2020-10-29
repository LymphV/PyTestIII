'''

有道翻译同义词
youdaoSynonym

==============

>>>yd = YoudaoSynonym() ###打开浏览器，打开有道翻译网页
>>>yd.getSynonyms('光学计算') ###生成同义词集
{'Optical computing', 'optical calculation', 'optical computing'}
>>>yd.close() ###关闭浏览器
'''

if '.' in __name__:
    from .driverOps import getDriver, waitTillOpen 
    from .cfg import home
else:
    from driverOps import getDriver, waitTillOpen
    from cfg import home


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
    
    __version__ = 20201029
    __author__ = 'LymphV@163.com'

    def __init__ (this, page = home):
        '''
        YoudaoSynonym初始化
        
        Parameters
        ----------
        page : 有道翻译网址，默认为cfg.py中的home
        '''
        this.__dv = None
        this.start(page)
    
    
    def start (this, page = home):
        '''
        打开有道翻译网址
        
        Parameters
        ----------
        page : 有道翻译网址，默认为cfg.py中的home
        '''
        if not page: return
        if not this.__dv:
            this.__dv = getDriver()
        this.__dv.get(page)
    
    def __getSynonyms (this, s : str):
        '''
        使用有道翻译获得同义词集
        '''
        dv = this.__dv
        dv.refresh()
        pathInput = '//textarea[@class="input__original__area"]'
        pathAnswer = '//div[@class="input__target__text"]/p/span'
        pathSuggest = '//*[@systemname="sys%d"]'
        pathRelative = '//div[@class="dict__relative"]/*'
        
        
        ###输入
        waitTillOpen(dv, 10, value=pathInput)
        ipts = dv.find_elements_by_xpath(pathInput)
        assert ipts, 'no input area found'
        
        ipt = ipts[0]
        ipt.clear()
        ipt.send_keys(s)
        
        rst = set()
        
        ###翻译结果
        waitTillOpen(dv, value=pathAnswer)
        ans = dv.find_elements_by_xpath(pathAnswer)
        rst |= {x.text for x in ans}
        if ans:
            ###翻译改进结果
            ans[0].click()
            for i in range(1,1000):
                sug = dv.find_elements_by_xpath(pathSuggest % i)
                if not sug: break
                rst |= {x.text for x in sug}
        
        ###翻译相关结果
        relative = dv.find_elements_by_xpath(pathRelative)
        rst |= {x.text for x in relative}
        return rst
    
    def __filter (this, s : str) -> set:
        '''
        过滤器
        过滤掉短语中的标点符号、停用词、词性、专业标志等
        ····待开发
        '''
        s = s.strip()
        return {s} if s else set()
        
    
    def getSynonyms (this, s : str) -> set:
        '''
        获取中文短语的英语同义词集合
        
        Parameters
        ----------
        s : 中文短语
        
        Returns
        -------
        getSynonyms : 英文同义词集合
        '''
        syns = this.__getSynonyms(s)
        rst = set()
        for s in syns:
            rst |= this.__filter(s)
        return rst
    def close (this):
        '''
        关闭浏览器，必须
        '''
        this.__dv.quit()
        this.__dv = None