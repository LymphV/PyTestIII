'''

更新关键词

-------------------

update : 检索一个关键词，并更新所有检索到的企业
'''

from math import ceil

if '.' in __name__:
    from .cfg import maxSearchPage as maxPage, nMaxFail
    from .cfg import ifSearch, ifTrademarkSearch, ifPatentSearch
    from .utils import ourError, ourLog, frmt, none2list
    from .mysqlInserter import checkKeyword, MysqlUpdateTimeInserter
    from .tycAPI import TycAPI
    from .enterpriseInfo import EnterpriseInfo, enterprisesInfo
else:
    from cfg import maxSearchPage as maxPage, nMaxFail
    from cfg import ifSearch, ifTrademarkSearch, ifPatentSearch
    from utils import ourError, ourLog, frmt, none2list
    from mysqlInserter import checkKeyword, MysqlUpdateTimeInserter
    from tycAPI import TycAPI
    from enterpriseInfo import EnterpriseInfo, enterprisesInfo

from vUtil.vTqdm import tqdm, trange

class UpdateKeyword:
    '''

    更新关键词

    -------------------

    update : 检索一个关键词，并更新所有检索到的企业
    '''

    __version__ = 20210831
    __author__ = 'LymphV@163.com'
    
    def __init__ (this, keyword):
        this.keyword = keyword
        this.check = checkKeyword(keyword)
    def __useAPI (this, api, *args):
        '''
        调用API并传入参数
        '''
        for i in range(nMaxFail):
            try:
                rst = api(*args)
                errorCode = rst.get('error_code', 0)
                reason = rst.get('reason', '')
                if errorCode:
                    ourError(f'{this.keyword}', f'use api({api.__name__}) error', f'code({errorCode}) reason({reason})')
                    continue
                return rst
            except KeyboardInterrupt as e:
                ourError(f'{this.keyword}', f'use api({api.__name__}) error', repr(e))
                raise e
            except Exception as e:
                ourError(f'{this.keyword}', f'use api({api.__name__}) error', repr(e))
        else:
            ourError(f'{this.keyword}', f'use api({api.__name__}) error', 'api max fail')
            return {}

    def __usePagesAPI (this, api):
        '''
        调用API并自动翻页，翻页最大页码为maxPage
        '''
        rst = [this.__useAPI(api,this.keyword)]
        total = 0
        try:
            total = int(rst[0].get('total', 0))
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            ourError(f'{this.keyword}', f'''read total error#{rst.get('total', 0)}''', repr(e))
        
        ###不限制翻页时使用一个足够大的页数
        mp = (1 << 64) if not maxPage or maxPage < 0 else maxPage
        if total is not None: mp = min(mp, ceil(total / 20))
        
        for i in range(2, mp + 1):
            rst += [this.__useAPI(api, this.keyword, i)]
        return rst
        
    def update (this, cnt=None, tq=None):
        '''
        检索一个关键词，并更新所有检索到的企业
        '''
        tyc = TycAPI()
        
        if this.check: return tyc.count
        
        keyword = this.keyword
        if cnt is None: cnt = {}
        
        try:
            apiCount = {}
            frmt(f'({repr(keyword)})获取企业id列表', tqdm=tq, end = ' ' * 10 + '\r')
            
            search = this.__usePagesAPI(tyc.search) if ifSearch else []
            trademarkSearch = this.__usePagesAPI(tyc.trademarkSearch) if ifTrademarkSearch else []
            patentSearch = this.__usePagesAPI(tyc.patentSearch) if ifPatentSearch else []
            
            frmt(f'({repr(keyword)})获取企业id列表完毕', tqdm=tq, end = ' ' * 10 + '\r')
            
            ids = []
            search = [y for x in search for y in none2list(x.get('items', []))]
            #search = search.get('items', [])
            ids += [x.get('id', None) for x in search]
            
            
            trademarkSearch = [y for x in trademarkSearch for y in none2list(x.get('items', []))]
            ids += [y.get('cgid', None) for x in trademarkSearch for y in none2list(x.get('companies', []))]
            
            patentSearch = [y for x in patentSearch for y in none2list(x.get('items', []))]
            ids += [y.get('cgid', None) for x in patentSearch for y in none2list(x.get('companies', []))]
            
            ids = {x for x in ids if x is not None}
            ourLog (f'{keyword}', '获取企业id列表', len(ids))
            
            enterprisesInfo(ids, apiCount=apiCount, keyword=keyword, leave=False)
        except KeyboardInterrupt as e:
            raise e
        finally:
            tot = sum(apiCount.values()) + tyc.count
            cnt[keyword] = tot
            
            ourLog (f'{keyword}', 'api调用次数', f'检索({tyc.count}) 企业({apiCount}) 总计({tot})')
        
        MysqlUpdateTimeInserter(tyc.now).insertKeyword(keyword)
        return tot
    