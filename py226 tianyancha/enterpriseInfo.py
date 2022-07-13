'''

企业信息

-------------------

getEnterpriseInfo : 调用API获得企业信息
saveEnterpriseInfo : 企业信息入库
'''

from math import ceil

if '.' in __name__:
    from .cfg import maxPage, ifTeamMember, ifProduct, ifTrademark, ifPatent, ifSoftwareCopyright, ifWebsite
    from .utils import ourError, ourLog, frmt, none2list, none2dict
    from .mysqlInserter import checkEnterprise, MysqlUpdateTimeInserter, insertStaffs
    from .mysqlInserter import insertHuman, insertTeamMembers, insertProducts
    from .mysqlInserter import insertTrademarks, insertPatents
    from .mysqlInserter import insertSoftwareCopyrights, insertWebsites
    from .tycAPI import TycAPI
else:
    from cfg import maxPage, ifTeamMember, ifProduct, ifTrademark, ifPatent, ifSoftwareCopyright, ifWebsite
    from utils import ourError, ourLog, frmt, none2list, none2dict
    from mysqlInserter import checkEnterprise, MysqlUpdateTimeInserter, insertStaffs
    from mysqlInserter import insertHuman, insertTeamMembers, insertProducts
    from mysqlInserter import insertTrademarks, insertPatents
    from mysqlInserter import insertSoftwareCopyrights, insertWebsites
    from tycAPI import TycAPI


class EnterpriseInfo:
    '''

    企业信息

    -------------------

    getEnterpriseInfo : 调用API获得企业信息
    saveEnterpriseInfo : 企业信息入库
    '''


    __version__ = 20210415
    __author__ = 'LymphV@163.com'
    
    def __init__ (this, id, keyword=None):
        this.id = id
        this.keyword = keyword
        this.enterprise = None
        this.staffs = []
        this.humans = []
        this.teamMembers = []
        this.products = []
        this.trademarks = []
        this.patents = []
        this.softwareCopyrights = []
        this.websites = []
        this.check = checkEnterprise(id)
        this.now = None
        


    def __useAPI (this, api, *args):
        '''
        调用API并传入参数
        '''
        id = this.id
        while 1:
            try:
                rst = api(*args)
                errorCode = rst.get('error_code', 0)
                reason = rst.get('reason', '')
                if errorCode:
                    ourError(f'{this.keyword}&{id}', f'code({errorCode}) reason({reason})', f'use api({api.__name__}) error')
                    continue
                return rst
            except KeyboardInterrupt as e:
                ourError(f'{this.keyword}&{id}', str(e), f'use api({api.__name__}) error')
                raise e
            except Exception as e:
                ourError(f'{this.keyword}&{id}', str(e), f'use api({api.__name__}) error')

    def __usePagesAPI (this, api):
        '''
        调用API并自动翻页，翻页最大页码为maxPage
        '''
        id = this.id
        rst = [this.__useAPI(api,id)]
        total = 0
        try:
            total = int(rst[0].get('total', 0))
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            ourError(f'{this.keyword}&{id}', str(e), f'''read total error#{rst.get('total', 0)}''')
        
        ###不限制翻页时使用一个足够大的页数
        mp = (1 << 64) if not maxPage or maxPage < 0 else maxPage
        if total: mp = min(mp, ceil(total / 20))
        
        for i in range(2, mp + 1):
            rst += [this.__useAPI(api, id, i)]
        return rst
    


    def getEnterpriseInfo (this):
        '''
        调用API获得企业信息
        '''
        if this.check: return 0
        
        id = this.id
        tyc = TycAPI()
    
        frmt(f'{this.keyword}&{id}', '调用API', end = ' ' * 3 + '\r')
        ourLog (f'{this.keyword}&{id}', '调用API')
        
        frmt(f'{this.keyword}&{id}', '调用baseInfo', end = ' ' * 3 + '\r')
        baseInfo = this.__useAPI(tyc.baseInfo, id)
        
        frmt(f'{this.keyword}&{id}', '调用teamMember', end = ' ' * 3 + '\r')
        teamMember = this.__usePagesAPI(tyc.teamMember) if ifTeamMember else [{}]
        
        frmt(f'{this.keyword}&{id}', '调用product', end = ' ' * 3 + '\r')
        product = this.__usePagesAPI(tyc.product) if ifProduct else [{}]
        
        frmt(f'{this.keyword}&{id}', '调用trademark', end = ' ' * 3 + '\r')
        trademark = this.__usePagesAPI(tyc.trademark) if ifTrademark else [{}]
        
        frmt(f'{this.keyword}&{id}', '调用patent', end = ' ' * 3 + '\r')
        patent = this.__usePagesAPI(tyc.patent) if ifPatent else [{}]
        
        frmt(f'{this.keyword}&{id}', '调用softwareCopyright', end = ' ' * 3 + '\r')
        softwareCopyright = this.__usePagesAPI(tyc.softwareCopyright) if ifSoftwareCopyright else [{}]
        
        frmt(f'{this.keyword}&{id}', '调用website', end = ' ' * 3 + '\r')
        website = this.__usePagesAPI(tyc.website) if ifWebsite else [{}]
        
        frmt(f'{this.keyword}&{id}', '数据获取完成', end = ' ' * 3 + '\r')
        ourLog (f'{this.keyword}&{id}', '数据获取完成')
        
        staffList = none2dict(baseInfo.get('staffList', {}))
        
        this.enterprise = {
            'id' : id,
            'regNumber' : baseInfo.get('regNumber', None), 
            'creditCode' : baseInfo.get('creditCode', None), 
            'taxNumber' : baseInfo.get('taxNumber', None), 
            'name' : baseInfo.get('name', None), 
            'name_en' : baseInfo.get('property3', None), 
            'alias' : baseInfo.get('alias', None), 
            'historyNames' : baseInfo.get('historyNames', None), 
            'historyNameList' : baseInfo.get('historyNameList', None), 
            'legalPersonName' : baseInfo.get('legalPersonName', None), 
            'regCapital' : baseInfo.get('regCapital', None), 
            'industry' : baseInfo.get('industry', None), 
            'regLocation' : baseInfo.get('regLocation', None), 
            'businessScope' : baseInfo.get('businessScope', None), 
            'phoneNumber' : baseInfo.get('phoneNumber', None), 
            'websiteList' : baseInfo.get('websiteList', None), 
            'email' : baseInfo.get('email', None), 
            'establishmentTime' : baseInfo.get('fromTime', None),
            'staffNumRange' : baseInfo.get('staffNumRange', None),
            'nStaff' : staffList.get('total',None),
            'nTeamMember' : teamMember[0].get('total',None), 
            'nProduct' : product[0].get('total',None), 
            'nTrademark' : trademark[0].get('total',None), 
            'nPatent' : patent[0].get('total',None),
            'nSoftwareCopyright' : softwareCopyright[0].get('total',None), 
            'nWebsite' : website[0].get('total',None)
        }
        
        staffList = none2list(staffList.get('result', []))
        this.staffs = [
            (
                x.get('id',None), 
                x.get('name', None), 
                x.get('type',None), 
                x.get('typeJoin',None)
            ) for x in staffList
        ]
        
        teamMember = [y for x in teamMember for y in none2list(x.get('items', []))]
        this.humans = [{
                        'id' : x.get('id', None),
                        'name' : x.get('name', None)
                    } for x in staffList] + [{
                        'id' : x.get('id', None),
                        'name' : x.get('name', None),
                        'icon' : x.get('iconOssPath', None),
                        'desc' : x.get('desc', None)
                    } for x in teamMember]
        
        this.teamMembers = [
            (
                x.get('hid', None), 
                x.get('name', None), 
                x.get('isDimission', None), 
                x.get('title', None),
                x.get('iconOssPath', None),
                x.get('desc', None)
            ) for x in teamMember
        ]
        
        product = [y for x in product for y in none2list(x.get('items', []))]
        this.products = [
            (
                x.get('hangye', None), 
                x.get('yewu', None),
                x.get('product', None), 
                x.get('logo', None), 
                x.get('setupDate', None)
            ) for x in product
        ]
        
        trademark = [y for x in trademark for y in none2list(x.get('items', []))]
        this.trademarks = [
            (
                x.get('id', None), 
                x.get('intCls', None),
                x.get('tmName', None), 
                x.get('regNo', None), 
                x.get('applicantCn', None),
                x.get('tmPic', None)
            ) for x in trademark
        ]
        
        patent = [y for x in patent for y in none2list(x.get('items', []))]
        this.patents = [
            (
                x.get('id', None),
                x.get('uuid', None),
                x.get('title', None),
                x.get('appnumber', None),
                x.get('pubnumber', None),
                x.get('patentNum', None),
                x.get('allCatNum', None),
                x.get('lawStatus', None),
                x.get('abstracts', None),
                x.get('applicationTime', None),
                x.get('pubDate', None),
                x.get('applicationPublishTime', None),
                x.get('inventor', None),
                x.get('applicantname', None),
                x.get('applicationName', None),
                x.get('agent', None),
                x.get('agency', None),
                x.get('address', None),
                x.get('patenttype', None)
            ) for x in patent
        ]
        
        softwareCopyright = [y for x in softwareCopyright for y in none2list(x.get('items', []))]
        this.softwareCopyrights = [
            (
                x.get('id', None),
                x.get('regnum', None),
                x.get('version', None),
                x.get('fullname', None),
                x.get('simplename', None),
                x.get('regtime', None),
                x.get('publishtime', None),
                x.get('eventTime', None),
                x.get('authorNationality', None)
            ) for x in softwareCopyright
        ]
        
        website = [y for x in website for y in none2list(x.get('items', []))]
        this.websites = [
            (
                x.get('webName', None),
                x.get('ym', None),
                x.get('webSite', None),
                x.get('liscense', None),
                x.get('companyName', None)
            ) for x in website
        ]
    
        frmt(f'{this.keyword}&{id}', '数据整理完成', end = ' ' * 3 + '\r')
        ourLog (f'{this.keyword}&{id}', '数据整理完成')
        this.now = tyc.now
        return tyc.count

    def saveEnterpriseInfo (this, db):
        '''
        企业信息入库
        '''
        if this.check or this.enterprise is None: return
        
        id = this.id
        frmt(f'{this.keyword}&{id}', '插入数据库', end = ' ' * 3 + '\r')
        ourLog (f'{this.keyword}&{id}', '插入数据库')
        
        MysqlUpdateTimeInserter(this.now).insertEnterprise(**this.enterprise)
        insertStaffs(id, this.staffs)
        for x in this.humans: insertHuman(**x)
        insertTeamMembers(id, this.teamMembers)
        insertProducts(id, this.products)
        insertTrademarks(id, this.trademarks)
        insertPatents(id, this.patents)
        insertSoftwareCopyrights(id, this.softwareCopyrights)
        insertWebsites(id, this.websites)
        
        db.commit()
