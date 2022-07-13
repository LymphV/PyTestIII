'''

更新关键词

-------------------

update : 检索一个关键词，并更新所有检索到的企业
'''

from math import ceil

if '.' in __name__:
    from .cfg import tqdmNcols as ncols, maxPage, ifSearch, ifTrademarkSearch, ifPatentSearch
    from .utils import ourError, ourLog, frmt, typeOfScript, none2list
    from .mysqlInserter import checkKeyword, MysqlUpdateTimeInserter
    from .tycAPI import TycAPI
    from .enterpriseInfo import EnterpriseInfo
else:
    from cfg import tqdmNcols as ncols, maxPage, ifSearch, ifTrademarkSearch, ifPatentSearch
    from utils import ourError, ourLog, frmt, typeOfScript, none2list
    from mysqlInserter import checkKeyword, MysqlUpdateTimeInserter
    from tycAPI import TycAPI
    from enterpriseInfo import EnterpriseInfo

if typeOfScript() == 'jupyter':
    from tqdm.notebook import tqdm, trange
else:
    from tqdm import tqdm, trange


class UpdateKeyword:
    '''

    更新关键词

    -------------------

    update : 检索一个关键词，并更新所有检索到的企业
    '''

    __version__ = 20210330
    __author__ = 'LymphV@163.com'
    
    def __init__ (this, keyword):
        this.keyword = keyword
        this.check = checkKeyword(keyword)
    def __useAPI (this, api, *args):
        '''
        调用API并传入参数
        '''
        while 1:
            try:
                rst = api(*args)
                errorCode = rst.get('error_code', 0)
                reason = rst.get('reason', '')
                if errorCode:
                    ourError(f'{this.keyword}', f'code({errorCode}) reason({reason})', f'use api({api.__name__}) error')
                    continue
                return rst
            except KeyboardInterrupt as e:
                ourError(f'{this.keyword}', str(e), f'use api({api.__name__}) error')
                raise e
            except Exception as e:
                ourError(f'{this.keyword}', str(e), f'use api({api.__name__}) error')

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
            ourError(f'{this.keyword}', str(e), f'''read total error#{rst.get('total', 0)}''')
        
        ###不限制翻页时使用一个足够大的页数
        mp = (1 << 64) if not maxPage or maxPage < 0 else maxPage
        if total: mp = min(mp, ceil(total / 20))
        
        for i in range(2, mp + 1):
            rst += [this.__useAPI(api, this.keyword, i)]
        return rst
        
    def update (this, db):
        '''
        检索一个关键词，并更新所有检索到的企业
        '''
        if this.check: return 0
        
        try:
            apiCount = []
            tyc = TycAPI()
            
            frmt('获取企业id列表', end = ' ' * 10 + '\r')
            ourLog (f'{this.keyword}', '获取企业id列表')
            
            search = this.__useAPI(tyc.search, this.keyword) if ifSearch else {}
            trademarkSearch = this.__usePagesAPI(tyc.trademarkSearch) if ifTrademarkSearch else []
            patentSearch = this.__usePagesAPI(tyc.patentSearch) if ifPatentSearch else []
            
            frmt('获取企业id列表完毕', end = ' ' * 10 + '\r')
            
            ids = []
            search = search.get('items', [])
            ids += [x.get('id', None) for x in search]
            
            
            trademarkSearch = [y for x in trademarkSearch for y in none2list(x.get('items', []))]
            ids += [y.get('cgid', None) for x in trademarkSearch for y in none2list(x.get('companies', []))]
            
            patentSearch = [y for x in patentSearch for y in none2list(x.get('items', []))]
            ids += [y.get('cgid', None) for x in patentSearch for y in none2list(x.get('companies', []))]
            
            ids = {x for x in ids if x is not None}
            for id in tqdm(ids, ncols=ncols, leave=False):
                epi = EnterpriseInfo(id, this.keyword)
                cnt = epi.getEnterpriseInfo()
                apiCount += [cnt]
                epi.saveEnterpriseInfo(db)
                
                #if cnt == 0:
                #    ourLog(f'{this.keyword}&{id}', 'api调用次数0')
        except KeyboardInterrupt as e:
            raise e
        finally:
            ourLog (f'{this.keyword}', f'检索({tyc.count}) 企业({apiCount}) 总计({sum(apiCount) + tyc.count})','api调用次数')
        
        MysqlUpdateTimeInserter(tyc.now).insertKeyword(this.keyword)
        db.commit()
        return sum(apiCount) + tyc.count
    