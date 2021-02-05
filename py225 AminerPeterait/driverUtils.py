'''

整理了一些selenium webdriver的常用读取文本操作

----------------------------

getTextByXpath : 由xpath路径获取文本，包括对元素查找相对路径
getAttributeByXpath : 由xpath路径获取属性，包括对元素查找相对路径
getTextById : 由id获取文本
getTextsByXpath : 由xpath路径获取多个文本
'''

def getTextByXpath (dv, path):
    '''
    由xpath路径获取文本，包括对元素查找相对路径
    '''
    rst = dv.find_elements_by_xpath(path)
    if not rst: return None
    return rst[0].text

def getAttributeByXpath (dv, path, attribute):
    '''
    由xpath路径获取属性，包括对元素查找相对路径
    '''
    rst = dv.find_elements_by_xpath(path)
    if not rst: return None
    return rst[0].get_attribute(attribute)

def getTextById (dv, tid):
    '''
    由id获取文本
    '''
    rst = dv.find_elements_by_id(tid)
    if not rst: return None
    return rst[0].text

def getTextsByXpath (dv, path):
    '''
    由xpath路径获取多个文本
    '''
    rst = dv.find_elements_by_xpath(path)
    return [x.text for x in rst]

