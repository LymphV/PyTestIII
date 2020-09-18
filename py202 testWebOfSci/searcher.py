'''

在搜索页的一些操作
webdriver当前标签页为搜索页，当前版本搜索方式为“基本检索”

------------------

selectDatabase : 选择数据库
selectSpan : 选择起止时间
search : 输入关键词并进行搜索

'''

from selenium.webdriver.common.keys import Keys


class DatabaseIndex:
    '''
    数据库选项的下标
    ----------------
    ALL : 所有数据库
    WOS : WOS核心合集
    CHI : 中国科学引文数据库
    CCC : Current Contents Connect
    DII : Derwent Innovations Index
    KKJ : Kci-Korean Journal Database
    MED : Medline
    RSC : Russian Science Citation Index
    SCI : Scielo Citation Index
    '''
    ALL = 0 ###所有数据库
    WOS = 1 ###WOS核心合集
    CHI = 2 ###中国科学引文数据库
    CCC = 3 ###Current Contents Connect
    DII = 4 ###Derwent Innovations Index
    KKJ = 5 ###Kci-Korean Journal Database
    MED = 6 ###Medline
    RSC = 7 ###Russian Science Citation Index
    SCI = 8 ###Scielo Citation Index


class SpanIndex:
    '''
    时间跨度选项的下标
    ------------------
    ALL : 所有年份
    R5Y : 最近五年
    CUY : 本年迄今
    R4W : 最近四周
    R2W : 最近二周
    CUW : 本周
    CTM : 自定义年份范围
    '''
    ALL = 1 ###所有年份
    R5Y = 2 ###最近五年
    CUY = 3 ###本年迄今
    R4W = 4 ###最近四周
    R2W = 5 ###最近二周
    CUW = 6 ###本周
    CTM = 'last()' ###自定义年份范围



def selectDatabase (dv):
    '''
    选择数据库
    当前版本需求为“wos核心合集”，故只能选择“wos核心合集”
    
    Parameters
    ----------
    dv : 当前handle是search页的webdriver
    '''
    
    sdbJs = 'databaseSelect(document.querySelector(".select-db select")[%s])'
    dv.execute_script(sdbJs % DatabaseIndex.WOS)




def selectSpan (dv, span = None):
    '''
    选择起止时间
    当前版本只提供起止年份功能
    
    Parameters
    ----------
    dv : 当前handle是search页的webdriver
    span : 起止时间对(startYear,endYear)，默认为None选择wos的所有年份
    
    Raise
    -----
    AssertionError : 当起止时间对wos非法时抛出错误
    '''
    
    ###选择时间跨度下拉框
    spanDdlPath = '//*[@name="range"]/following-sibling::*[1]'
    ###选择时间跨度
    spanPath = '//*[@class="select2-results__options"]/*[%s]'
    ###选择起止时间下拉框
    seyDdlPath = '//*[@name="%s"]/following-sibling::*[1]'
    ###选择起止时间输入框
    seyIptPath = '//*[@class="select2-search__field"]'
    ###选择警告框，当输入wos不允许的时间时会出现
    errorPath = '//*[@aria-live="assertive"]'
    
    ###默认选择“所有年份”
    if not span:
        ###点击时间跨度下拉框
        dv.find_element_by_xpath(spanDdlPath).click()
        ###点击时间跨度“所有年份”
        dv.find_element_by_xpath(spanPath % SpanIndex.ALL).click()
        return
    
    ###选择“自定义年份范围”
    startYear, endYear = span
    ###点击时间跨度下拉框
    dv.find_element_by_xpath(spanDdlPath).click()
    ###点击时间跨度“自定义年份范围”
    dv.find_element_by_xpath(spanPath % SpanIndex.CTM).click()
    
    ###点击起始时间下拉框
    dv.find_element_by_xpath(seyDdlPath % 'startYear').click()
    
    ###wos提供的最早时间
    if startYear is None:
        startYear = int(dv.find_element_by_xpath(spanPath % 1).text.strip())
    
    ###选择起始时间输入框，并输入起始时间
    inpStartYear = dv.find_element_by_xpath(seyIptPath)
    inpStartYear.clear()
    inpStartYear.send_keys(str(startYear))
    ###非法起始时间
    assert not dv.find_elements_by_xpath(errorPath), 'invalid start year'
    inpStartYear.send_keys(Keys.ENTER)
    
    ###点击终止时间输入框，并输入终止时间
    dv.find_element_by_xpath(seyDdlPath % 'endYear').click()
        
    ###wos提供的最晚时间
    if endYear is None:
        endYear = int(dv.find_element_by_xpath(spanPath % 1).text.strip())
        
    inpEndYear = dv.find_element_by_xpath(seyIptPath)
    inpEndYear.clear()
    inpEndYear.send_keys(str(endYear))
    ###非法终止时间
    assert not dv.find_elements_by_xpath(errorPath), 'invalid end year'
    inpEndYear.send_keys(Keys.ENTER)



def search (dv, keyWord):
    '''
    输入关键词并进行搜索
    
    Parameters
    ----------
    dv : 当前handle是search页的webdriver
    keyWord : 检索关键词
    '''

    inp = dv.find_element_by_name('value(input1)')
    inp.clear()
    inp.send_keys(keyWord)
    inp.send_keys(Keys.ENTER)

def ifSearchFailed (dv):
    '''
    检测是否检索失败
    
    Parameters
    ----------
    dv : 当前handle是search页的webdriver
    
    Returns
    -------
    ifSearchFailed : 检索失败则返回检索错误信息，否则返回''
    '''
    
    msgTags = dv.find_elements_by_class_name('errorMessage')
    return '' if not msgTags else msgTags[0].text.strip()
        




