'''

调用天眼查API
如果API返回的JSON存入文件，则重复调用时会直接读取updateGap以内的文件返回而不会真正再次调用API
如果savePath为False或None，则API返回的JSON不存入文件

-------------------

api : 调用API
search : 调用检索API
trademarkSearch : 调用商标垂搜API
patentSearch : 调用专利垂搜API
baseInfo : 调用基本信息（含主要人员）API
teamMember : 调用核心团队API
product : 调用企业业务API
trademark : 调用企业商标信息API
patent : 调用企业专利信息API
softwareCopyright : 调用软件著作权API
website : 调用网站备案API

'''


import requests
import os
from time import sleep, time
import json
from pandas._libs.tslibs.timedeltas import Timedelta as td
from pandas import Timestamp as ts
import numpy as np

if '.' in __name__:
    from .cfg import token, savePath, apiGap, updateGap
    from .utils import ourError, none2dict
else:
    from cfg import token, savePath, apiGap, updateGap
    from utils import ourError, none2dict

from vUtil.vFile import fprint
from vUtil.vTime import getNow

### 调用API的请求头
headers = {'Authorization' : token}
### 最近一次调用API的时间
now = 0

__path__  = os.path.dirname(os.path.abspath(__file__))


class TycAPI:
    '''

    调用天眼查API
    如果API返回的JSON存入文件，则重复调用时会直接读取updateGap以内的文件返回而不会真正再次调用API
    如果savePath为False或None，则API返回的JSON不存入文件

    -------------------

    api : 调用API
    search : 调用检索API
    trademarkSearch : 调用商标垂搜API
    patentSearch : 调用专利垂搜API
    baseInfo : 调用基本信息（含主要人员）API
    teamMember : 调用核心团队API
    product : 调用企业业务API
    trademark : 调用企业商标信息API
    patent : 调用企业专利信息API
    softwareCopyright : 调用软件著作权API
    website : 调用网站备案API

    '''
    
    __version__ = 20210830
    __author__ = 'LymphV@163.com'
    
    def initCount (*args):
        return np.array([0,0])
    
    def __init__ (this):
        ### 调用API次数
        this.count = this.initCount()
        ### 更新时间，取调用一组API的最早时间
        this.now = None
    
    def __str__ (this):
        return f'[TycAPI(use api count#{this.count})]'
    
    def __repr__ (this): return str(this)

    def api (this, page, file, folder, **kw):
        '''
        调用API
        如果API返回的JSON存入文件，则重复调用时会直接读取updateGap以内的文件返回而不会真正再次调用API
        如果savePath为False或None，则API返回的JSON不存入文件
    
        Parameters
        ----------
        page : API网址
        file : 保存JSON文件的文件名
        folder : 保存JSON文件的文件夹
        **kw : API参数
        
        
        Returns
        -------
        json : 返回JSON读取的API结果
        '''
        global now
        
        if not kw or not [v for v in kw.values() if v is not None]: return {}
        
        this.page = page = page + '?' + '&'.join([f'{k}={kw[k]}' for k in kw if kw[k] is not None])
        
        if savePath:
            if os.path.isabs(savePath):
                path = os.path.join(savePath, folder)
            else:
                path = os.path.join(__path__, savePath, folder)
            if not os.path.exists(path): os.makedirs(path)
            
            path = os.path.join(path,f'{file}.json')
            maxUpdateTime = ts(getNow()) - td(f'{updateGap}s')
        
        ### 如果已存储，则直接读取
            try:
                if os.path.exists(path) and maxUpdateTime < ts.fromtimestamp(os.path.getmtime(path)):
                    with open(path, 'r', encoding='utf-8') as f:
                        rst = json.load(f)
                    errorCode = rst.get('error_code', 0)
                                    
                    if not errorCode or errorCode == 300000:
                        ftime = str(ts.fromtimestamp(os.path.getmtime(path))).split('.')[0]
                        this.now = ftime if this.now is None else str(min(ts(this.now), ts(ftime)))
                        return {
                            0 : none2dict(rst.get('result', rst)),
                            300000 : {'total' : 0}
                        }.get(errorCode, rst)
            except KeyboardInterrupt as e: raise e
            except Exception as e: pass
        
        ### 调试文件读取时防止失败重复调用API
        #raise KeyboardInterrupt('file load error')
        
        while time() < now + apiGap: sleep(0.1)
        now = time()
        
        rst = requests.get(page, headers=headers)
        jrst = rst.json()
        errorCode = jrst.get('error_code', 0)
        
        if errorCode == 300001:
            sleep(apiGap)
        elif errorCode == 300004:
            sleep(apiGap)
        elif errorCode == 300005 or errorCode == 300011: ### 无权限访问此api
            reason = jrst.get('reason', '')
            ourError(f'{file}', f'use api({folder}) error', f'code({errorCode}) reason({reason})')
            jrst = {}
        
        
        elif errorCode == 300002:
            raise KeyboardInterrupt('账号失效')
        elif errorCode == 300003:
            raise KeyboardInterrupt('账号过期')
        
        elif errorCode == 300006:
            raise KeyboardInterrupt('余额不足')
        elif errorCode == 300007:
            raise KeyboardInterrupt('剩余次数不足')
            
        
        if not errorCode or errorCode == 300000:
            if not errorCode: this.count += np.array([1,1])
            else: this.count += np.array([1,0])
            if (savePath): 
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(rst.text + '\n')
        this.now = getNow() if this.now is None else str(min(ts(this.now), ts(getNow())))
        return {
            0 : none2dict(jrst.get('result', jrst)),
            300000 : {'total' : 0}
        }.get(jrst.get('error_code', 0), jrst)
        
    
    def search (this, keyword, pageNum=1):
        '''
        
        调用检索API
    
        Parameters
        ----------
        keyword : 关键词
        pageNum : 页码，默认为1
        
        Returns
        -------
        json : 返回JSON读取的API结果
        
        '''
        page = 'http://open.api.tianyancha.com/services/open/search/2.0'
        folder = 'search'
        return this.api(page, f'{keyword}#{pageNum}', folder, word=keyword, pageNum=pageNum)
    
    def trademarkSearch (this, keyword, pageNum=1):
        '''
        
        调用商标垂搜API
    
        Parameters
        ----------
        keyword : 关键词
        pageNum : 页码，默认为1
        
        Returns
        -------
        json : 返回JSON读取的API结果
        
        '''
        page = 'http://open.api.tianyancha.com/services/open/ipr/tm/search'
        folder = 'trademarkSearch'
        return this.api(page, f'{keyword}#{pageNum}', folder, keyword=keyword, pageNum=pageNum)
    
    def patentSearch (this, keyword, pageNum=1):
        '''
        
        调用专利垂搜API
    
        Parameters
        ----------
        keyword : 关键词
        pageNum : 页码，默认为1
        
        Returns
        -------
        json : 返回JSON读取的API结果
        
        '''
        page = 'http://open.api.tianyancha.com/services/open/ipr/patents/search'
        folder = 'patentSearch'
        return this.api(page, f'{keyword}#{pageNum}', folder, keyword=keyword, pageNum=pageNum)
    
    def baseInfo (this, keyword):
        '''
        
        调用基本信息（含主要人员）API
    
        Parameters
        ----------
        keyword : 关键词
        
        Returns
        -------
        json : 返回JSON读取的API结果
        
        '''
        page = 'http://open.api.tianyancha.com/services/open/ic/baseinfoV3/2.0'
        folder = 'baseInfo'
        return this.api(page, keyword, folder, keyword=keyword)
    
    def teamMember (this, keyword, pageNum=1):
        '''
        
        调用核心团队API
    
        Parameters
        ----------
        keyword : 关键词
        pageNum : 页码，默认为1
        
        Returns
        -------
        json : 返回JSON读取的API结果
        
        '''
        page = 'http://open.api.tianyancha.com/services/open/cd/findTeamMember/2.0'
        folder = 'teamMember'
        return this.api(page, f'{keyword}#{pageNum}', folder, keyword=keyword, pageNum=pageNum)

    def product (this, keyword, pageNum=1):
        '''
        
        调用企业业务API
    
        Parameters
        ----------
        keyword : 关键词
        pageNum : 页码，默认为1
        
        Returns
        -------
        json : 返回JSON读取的API结果
        
        '''
        page = 'http://open.api.tianyancha.com/services/open/cd/getProductInfo/2.0'
        folder = 'product'
        return this.api(page, f'{keyword}#{pageNum}', folder, keyword=keyword, pageNum=pageNum)
    
    
    def trademark (this, keyword, pageNum=1):
        '''
        
        调用企业商标信息API
    
        Parameters
        ----------
        keyword : 关键词
        pageNum : 页码，默认为1
        
        Returns
        -------
        json : 返回JSON读取的API结果
        
        '''
        page = 'http://open.api.tianyancha.com/services/open/ipr/tm/2.0'
        folder = 'trademark'
        return this.api(page, f'{keyword}#{pageNum}', folder, keyword=keyword, pageNum=pageNum)
    
    def patent (this, keyword, pageNum=1):
        '''
        
        调用企业专利信息API
    
        Parameters
        ----------
        keyword : 关键词
        pageNum : 页码，默认为1
        
        Returns
        -------
        json : 返回JSON读取的API结果
        
        '''
        page = 'http://open.api.tianyancha.com/services/open/ipr/patents/2.0'
        folder = 'patent'
        return this.api(page, f'{keyword}#{pageNum}', folder, keyword=keyword, pageNum=pageNum)

    def softwareCopyright (this, keyword, pageNum=1):
        '''
        
        调用软件著作权API
    
        Parameters
        ----------
        keyword : 关键词
        pageNum : 页码，默认为1
        
        Returns
        -------
        json : 返回JSON读取的API结果
        
        '''
        page = 'http://open.api.tianyancha.com/services/open/ipr/copyReg/2.0'
        folder = 'softwareCopyright'
        return this.api(page, f'{keyword}#{pageNum}', folder, keyword=keyword, pageNum=pageNum)
    
    def website (this, keyword, pageNum=1):
        '''
        
        调用网站备案API
    
        Parameters
        ----------
        keyword : 关键词
        pageNum : 页码，默认为1
        
        Returns
        -------
        json : 返回JSON读取的API结果
        
        '''
        page = 'http://open.api.tianyancha.com/services/open/ipr/icp/3.0'
        folder = 'website'
        return this.api(page, f'{keyword}#{pageNum}', folder, keyword=keyword, pageNum=pageNum)
    
    def xgBaseInfo (this, keyword):
        '''
        
        调用特殊企业基本信息API
    
        Parameters
        ----------
        keyword : 关键词
        
        Returns
        -------
        json : 返回JSON读取的API结果
        
        '''

        page = 'http://open.api.tianyancha.com/services/v4/open/xgbaseinfoV2'
        folder = 'xgBaseInfo'
        return this.api(page, keyword, folder, keyword=keyword)