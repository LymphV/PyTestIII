'''

从scholar页抽取字段
webdriver当前标签页为scholar页

------------------

getId : 抽取scholar的aminer id
getPortrait : 抽取scholar的头像并编码为base64
getName : 抽取scholar的(中文名,拼音)
getTitle : 抽取scholar的职称
getDepartment : 抽取scholar的机构
getPhone : 抽取scholar的电话
getEmail : 抽取scholar的email
getWebPages : 抽取scholar的主页
getFax : 抽取scholar的传真
getAddress : 抽取scholar的住址
getAwards : 抽取scholar的奖项
getTalentPools : 抽取scholar归属的人才库
getExperience : 抽取scholar的工作经历
getEducation : 抽取scholar的教育背景
getBrief : 抽取scholar的个人简介
getPapers : 抽取scholar的论文（按引用量降序的一页，以便去重）

'''


from urllib.request import urlopen
import base64
import re
from time import sleep
from urllib import error

if '.' in __name__:
    from .driverOps import waitTillOpen, waitTillLoaded
    from .utils import stdAminerId, rmUnseen
    from .driverUtils import getTextByXpath, getAttributeByXpath, getTextById, getTextsByXpath
    from .cfg import waitUnit, waitLoading
else:
    from driverOps import waitTillOpen, waitTillLoaded
    from utils import stdAminerId, rmUnseen
    from driverUtils import getTextByXpath, getAttributeByXpath, getTextById, getTextsByXpath
    from cfg import waitUnit, waitLoading



class AminerScholarExtracter:
    '''
    从scholar页抽取字段
    webdriver当前标签页为scholar页

    ------------------

    getId : 抽取scholar的aminer id
    getPortrait : 抽取scholar的头像并编码为base64
    getName : 抽取scholar的(中文名,拼音)
    getTitle : 抽取scholar的职称
    getDepartment : 抽取scholar的机构
    getPhone : 抽取scholar的电话
    getEmail : 抽取scholar的email
    getWebPages : 抽取scholar的主页
    getFax : 抽取scholar的传真
    getAddress : 抽取scholar的住址
    getAwards : 抽取scholar的奖项
    getTalentPools : 抽取scholar归属的人才库
    getExperience : 抽取scholar的工作经历
    getEducation : 抽取scholar的教育背景
    getBrief : 抽取scholar的个人简介
    getPapers : 抽取scholar的论文（按引用量降序的一页，以便去重）
    '''
    __verison__ = 20210205
    __author__ = "LymphV@163.com"
    def __init__ (this, dv):
        this.__dv = dv
    
    def __clickIfNotActive (this, element, secWait, pathWait, reClick=0):
        '''
        点击元素，如果元素不处于活跃状态的话，并等待直到一个路径的元素出现
        
        Parameters
        ----------
        
        element : 点击的元素
        secWait : 一次点击的最长等待时间
        pathWait : 等待加载的判断路径
        reClick : 重复点击次数，防止论文引用量排序点击没有反应，默认为0

        '''
        dv = this.__dv
#         dv.execute_script('arguments[0].scrollIntoView();', element)
        if 'active' not in element.get_attribute('class'): 
#             element.click()
            dv.execute_script('arguments[0].click();', element)
            sleep(waitUnit)
            waitTillOpen(dv, secWait, value=pathWait)
            for i in range(reClick):
                dv.execute_script('arguments[0].click();', element)
                sleep(waitUnit)
                waitTillOpen(dv, secWait, value=pathWait)
    
    
    def getId (this):
        '''
        抽取scholar的aminer id
        '''
        return stdAminerId(this.__dv.current_url.split('/')[-1])
    def getPortrait (this):
        '''
        抽取scholar的头像并编码为base64
        '''
        path =  '//*[contains(@class, "profile")]' \
                        '//*[contains(@class, "avatar")]' \
                        '//img[contains(@class, "avatar")]'
        portrait = getAttributeByXpath(this.__dv, path, 'src')
        if portrait is None or 'default' in portrait: return None
        try: 
            return base64.b64encode(urlopen(portrait).read()).decode('ascii')
        except error.HTTPError as e: return None
        except Exception as e: return e
    def getNameOld (this):
        '''
        已废除，抽取scholar的(中文名,拼音)
        '''
        #pathPinyin = '//h1[contains(@class,name)]/span/span[@class="sub"]'
        path = '//h1[contains(@class,"name")]/span'
        
        names = this.__dv.find_elements_by_xpath(path)
        if not names: return (None, None)
        rst = re.findall(r'([^()（）]+)[(（]?([^()（）]*)[)）]?', names[0].text)[0]
        return (rst[0], rst[1] if rst[1] else None)
    
    def getName (this):
        '''
        抽取scholar的(中文名,拼音)
        '''
        idName = 'scholar_name_LymphV'
        idPinyin = 'scholar_pinyin_LymphV'
        
        ###直接运行js会出现circular reference错误
        if getTextById(this.__dv, idName) is None:
            this.__dv.execute_script(f'''
                script= document.createElement('script');
                script.text = '\
                    sname = document.createElement("p");\
                    sname.setAttribute("id", "{idName}");\
                    sname.textContent = document.querySelector("h1[class*=name] span").childNodes[0].textContent;\
                    document.getElementsByTagName("body")[0].appendChild(sname);\
                    pyname = document.createElement("p");\
                    pyname.setAttribute("id", "{idPinyin}");\
                    pyname.textContent = document.querySelector("h1[class*=name] span span.sub").childNodes[1].textContent;\
                    document.getElementsByTagName("body")[0].appendChild(pyname);'
                document.getElementsByTagName('body')[0].appendChild(script);
            ''')
        return (getTextById(this.__dv, idName), getTextById(this.__dv, idPinyin))
        
    def getTitle (this):
        '''
        抽取scholar的职称
        '''
        path = '//*[contains(@class,"briefcase")]/../span'
        return getTextByXpath(this.__dv, path)
    def getDepartment (this):
        '''
        抽取scholar的机构
        '''
        path = '//*[contains(@class,"institution")]/../span'
        return getTextByXpath(this.__dv, path)
    def getPhone (this):
        '''
        抽取scholar的电话
        '''
        path = '//*[contains(@class,"phone")]/../span'
        return getTextByXpath(this.__dv, path)
    def getEmail (this):
        '''
        抽取scholar的email
        '''
        path = '//*[contains(@class,"envelope")]/../span'
        return getTextByXpath(this.__dv, path)
    def getWebPages (this):
        '''
        抽取scholar的主页
        '''
        path = '//*[contains(@class,"globe")]/../a'
        return getTextsByXpath(this.__dv, path)
    def getFax (this):
        '''
        抽取scholar的传真
        '''
        path = '//*[contains(@class,"fax")]/../span'
        return getTextByXpath(this.__dv, path)
    def getAddress (this):
        '''
        抽取scholar的住址
        '''
        path = '//*[contains(@class,"map-marker")]/../span'
        return getTextByXpath(this.__dv, path)
    def getAwards (this):
        '''
        抽取scholar的奖项
        '''
        path = '//*[contains(@class,"awards_title")]/..//img/..'
        return getTextsByXpath(this.__dv, path)
    def getTalentPools (this):
        '''
        抽取scholar归属的人才库
        '''
        path = '//*[contains(@class,"eb_title")]/../span'
        return getTextsByXpath(this.__dv, path)
    
    
    def getExperience (this):
        '''
        抽取scholar的工作经历
        '''
        pathBasic = '//*[contains(@class,"ant-tabs-nav-list")]/*[1]'
        path = '//*[contains(@class,"active")]//*[@class="aff_inst"]/div'
        basic = this.__dv.find_elements_by_xpath(pathBasic)
        if not basic: return None
        basic = basic[0]
        this.__clickIfNotActive(basic, waitLoading, path)
        return getTextByXpath(this.__dv, path)
    def getEducation (this):
        '''
        抽取scholar的教育背景
        '''
        pathBasic = '//*[contains(@class,"ant-tabs-nav-list")]/*[1]'
        path = '//*[contains(@class,"active")]//*[contains(@class,"education")]'
        basic = this.__dv.find_elements_by_xpath(pathBasic)
        if not basic: return None
        basic = basic[0]
        this.__clickIfNotActive(basic, waitLoading, path)
        return getTextByXpath(this.__dv, path)
    def getBrief (this):
        '''
        抽取scholar的个人简介
        '''
        pathBasic = '//*[contains(@class,"ant-tabs-nav-list")]/*[1]'
        path = '//*[contains(@class,"active")]//*[contains(@class,"bio")]'
        basic = this.__dv.find_elements_by_xpath(pathBasic)
        if not basic: return None
        basic = basic[0]
        this.__clickIfNotActive(basic, waitLoading, path)
        return getTextByXpath(this.__dv, path)
    
    def getPapers (this):
        '''
        抽取scholar的论文（按引用量降序的一页，以便去重）
        '''
        
        ###“学术成果”标签，可点击
        pathAchievements  = '//*[contains(@class,"ant-tabs-nav-list")]/*[2]'
        
        ###发表论文or科研项目
        pathPP = '//*[contains(@class,"ant-tabs-nav-list")]/*[2]/self::*[contains(@class,"active")]/../../../..//span[@class="title"]'
        ###“按引用量排序”标签，可点击
        pathRefSort = '//*[contains(@class,"pubs_sort_line")]/div/*[2]'
        
        ###论文标签
        pathPaper = '//*[contains(@class,"pubs_sort_line")]/div'\
                    '/*[2]/self::*[contains(@class,"active")]/../../../../..'\
                    '//*[@class="content"]'
        ###论文id相对路径
        pathId = '..'
        ###论文题目相对路径
        pathTitle = './/*[contains(@class,"title")]/span'
        ###论文作者相对路径
        pathAuthor = './/*[contains(@class,"authors")]'
        ###论文期刊相对路径
        pathVenue = './/*[contains(@class,"venue-line")]'
        ###论文引用量相对路径
        pathCited = './/*[@class="cited"]/strong'
        ###加载等待中
        pathLoading = '//*[contains(@class,"sk_chase")]'
        ###没有论文
        pathNodata = '//div[contains(@class,"profilePapers___1bMnJ")]//img[contains(@src,"noData")]'
        
        ###是否有论文
        pathHavePapers = '//div[contains(@class,"profilePapers___1bMnJ")]//*[@class="content"]'
        
        
        ###点击“学术成果”
        achievements = this.__dv.find_elements_by_xpath(pathAchievements)
        if not achievements: return []
        achievements = achievements[0]
        ###没有“学术成果”键
        if 'disabled' in achievements.get_attribute('class'):
            return []
        this.__clickIfNotActive(achievements, waitLoading, pathPP)
        
        ###点击“按引用量排序”
        if not this.__dv.find_elements_by_xpath(pathHavePapers): return []
        refSort = this.__dv.find_elements_by_xpath(pathRefSort)
        if not refSort: raise Exception("no sort by reference")
        refSort = refSort[0]
        this.__clickIfNotActive(refSort, waitLoading, pathPaper + '|' + pathNodata, 1)
        
        if not waitTillLoaded(this.__dv, waitLoading, value=pathLoading, waitUnit=waitUnit):
            raise Exception("load failed")
        
        if this.__dv.find_elements_by_xpath(pathNodata): return []
        
        ###抽取结果
        papers = this.__dv.find_elements_by_xpath(pathPaper)
        
        return [{
            "id" : stdAminerId(getAttributeByXpath(p, pathId, 'id')),
            "title" : getTextByXpath(p, pathTitle),
            "authors" : rmUnseen(getTextByXpath(p, pathAuthor)),
            "venue" : getTextByXpath(p, pathVenue),
            "cited" : getTextByXpath(p, pathCited)
        } for p in papers]
        