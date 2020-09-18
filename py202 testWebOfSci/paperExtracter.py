'''

从paper页抽取字段
webdriver当前标签页为paper页

------------------

extractValues : 从paper页抽取字段

'''


import re


def __cleanAuthor (txt):
    '''
    清洗作者，去除“作者：”，去除中括号角标，去除末尾的“...更少内容”
    '''
    
    rst = re.sub(r'^.*?[:：]', '', txt)
    rst = re.sub(r'\[[\s\d,]*?\]', '', rst)
    return re.sub(r'\.\.\..*?$', '', rst)



def extractValues (dv):
    '''
    从paper页抽取title，authors，cauthors，email字段
    
    Parameters
    ----------
    dv : 当前handle是paper页的webdriver
    
    Returns
    -------
    extractValues : 没有email为无效页面返回None，否则字段为返回值的各属性
    '''
    
    def rst(): pass
    
    ###可能因为作者过多而折叠，如果折叠，点击“更多内容”
    moreAuthor = dv.find_elements_by_name('show_more_authors_authors_txt_label')
    if moreAuthor and moreAuthor[0].get_attribute('style') == 'display: inline;': 
        print(moreAuthor[0].get_attribute('style'))
        moreAuthor[0].click()
    
    ###标签xpath
    aPath = '//div[@class="block-record-info"]/p[@class="FR_field"]'
    cPath = '//a[@class="snowplow-author-email-addresses"]/../..'
    ePath = '//a[@class="snowplow-author-email-addresses"]'
    
    ###获取所在位置的标签，通讯作者因为需要正则匹配所以取了更高层的结点
    title = dv.find_elements_by_class_name('title')
    authors = dv.find_elements_by_xpath(aPath)
    cauthors = dv.find_elements_by_xpath(cPath)
    email = dv.find_elements_by_xpath(ePath)
    
    ###没有email为无效页面
    if not email: return None
    
    ###通信作者正则
    caReg = r'[:：]\s*(.*)\s\(corresponding author\)'
    
    ###获取对应文本，通讯作者去重因为见到有文章一个通讯作者写了两次
    rst.title = '' if not title else title[0].text
    rst.authors = '' if not authors else __cleanAuthor(authors[0].text)
    rst.cauthors = '' if not cauthors else ';'.join(set(re.findall(caReg, cauthors[0].text)))
    rst.email = email[0].text
    return rst