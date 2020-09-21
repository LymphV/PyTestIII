'''

整理了一些selenium webdriver的常用操作
----------------------------
getDriver : 获取webdriver
newLabel : 打开新的标签页
switchLabel : 切换标签页
waitTillOpen : 等待页面打开

'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC

if '.' in __name__:
    from .cfg import userAgent
else:
    from cfg import userAgent

def getDriver (ifHeadless = True):
    '''
    获取webdriver
    
    Parameters
    ----------
    ifHeadless : 是否为无头浏览器，默认为True，使用有头浏览器便于调试
    
    Returns
    -------
    getDriver : 一个调用chrome浏览器的selenium webdriver
    '''
    
    if not ifHeadless: return webdriver.Chrome()
    
    ###无头浏览器需要切换user agent为有头谷歌浏览器的user agent
    #  因为使用无头浏览器user agent时wos加载超时
    #  推测因为反爬防止无头浏览器访问
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--headless')
    options.add_argument('user-agent="%s"' % userAgent)
    
    ###据说可以加快网页打开速度
    # options.binary_location = "C:/Users/ict/AppData/Local/Google/Chrome/Application/chrome.exe"
    # options.add_argument('--disable-gpu')
    # prefs = {
    #         'profile.default_content_setting_values': {
    #             'images': 2,
    #             'permissions.default.stylesheet':2,
    #             'javascript': 2
    #         }
    #     }
    # options.add_experimental_option('prefs', prefs)
    
    rst = webdriver.Chrome(options=options)
    rst.set_window_size(1366,850)
    return rst
    

def newLabel (dv, url = ''):
    '''
    打开新的标签页
    无论用户看到的是否是新打开的标签页
    driver的当前标签页都不改变
    
    Parameters
    ----------
    dv : webdriver
    url : 新标签打开的页面，默认为空
    '''
    dv.execute_script('window.open("%s")' % url)    



def switchLabel (dv, n):
    '''
    切换标签页
    
    Parameters
    ----------
    dv : webdriver
    n : 标签序号，按标签创建顺序先后排序，不是用户看到的浏览器中的标签顺序
    '''
    dv.switch_to.window(dv.window_handles[n])


def waitTillOpen (dv, secs = 60, by = By.XPATH, value = None):
    '''
    等待页面打开
    dv：webdriver
    secs：等待最长时间（秒）， 默认60s
    '''
    wosHomePath = '//a[@class="snowplow-banner-wosLogo"]'
    Wait(dv, secs).until(EC.presence_of_element_located((by, value if value else wosHomePath)))