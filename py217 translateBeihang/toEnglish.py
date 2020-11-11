'''
将字符串翻译到英文

>>>from toEnglish import toEnglish
>>>toEnglish('你好')
'Hello there'

==========

toEnglish(s:str)->str 将字符串翻译到英文
setIfPrint(ip:bool) 设置ifPrint网络故障时是否打印，默认打印
setAutoReset(ar:bool) 设置autoReset网络故障重试次数是否自动清零，当ifPrint设置为False实质上autoReset无意义，默认自动清零
getIRetry() 获取网络故障重试次数
resetIRetry() 网络故障重试次数清零
addLog(f) 使用用于报错的回调函数
'''

import re
from time import time, sleep

if '.' in __name__:
    from .translate import translate
    from .detect import isEnglish, hasChinese, countChinese
else:
    from translate import translate
    from detect import isEnglish, hasChinese, countChinese



###用于报错的log回调函数
log = [lambda s : None]
def addLog (f): log.append(f)

ifPrint = True
def setIfPrint (ip):
    '''
    设置ifPrint网络故障时是否打印
    '''
    global ifPrint
    ifPrint = ip


autoReset = True
def setAutoReset(ar):
    '''
    设置autoReset网络故障重试次数是否自动清零
    当ifPrint设置为False实质上autoReset无意义
    '''
    global autoReset
    autoReset = ar



def prnt (*x, **y):
    if ifPrint: print(*x, **y)


def wait (t, s = 'waiting'):
    '''
    网络等待
    '''
    for i in range(4 * t):
        prnt (s, ['-','\\','|','/'][i%4], end='\r')
        sleep(0.25)


iRetry = 0
def getIRetry (): 
    '''
    获取网络故障重试次数
    '''
    return iRetry
def resetIRetry():
    '''
    网络故障重试次数清零
    '''
    global iRetry
    iRetry = 0

lastTrans = 0
transGap = 2 ###两次调用谷歌翻译的间隔
def trans (s):
    global lastTrans
    global iRetry
    while time() < lastTrans + transGap: sleep(0.25)
    while 1:
        if autoReset: iRetry = 0
        try:
            return translate(s, src='zh-cn') if hasChinese(s) else translate(s)
        except KeyboardInterrupt as e: raise e
        except:
            if not iRetry: prnt()
            wait(10, 'network error, waiting')
            iRetry += 1
            prnt('network error, retrying  ', iRetry, end='\r')
        else: 
            #if iRetry: prnt()
            break
    lastTrans = time()


MAX_CH = 1650 ### 1650 * 3 < 5000 一次翻译的最长字数
def toEnglish (s, ifTransPeriod = False, ifTransSemicolon = False):
    '''
    对外接口，将字符串s翻译到英文
    '''
    if s is None: return ''
    if type(s) is not str: return ''
    s = re.sub(r'&#?\S{1,10}?;', ' ', s)
    s = re.sub(r'</?\S{1,10}?>', '', s)
    s = re.sub(r'[\t ]+', ' ', s)
    
    if isEnglish(s): return s
    
    l = s.split('\n')
    ind, txt, cnt = [], [], 0
    
    for i in range(len(l) + 1):
        if i < len(l) and isEnglish(l[i]): continue
        if i == len(l) or MAX_CH < cnt + len(l[i]) + 1:
#             prnt('hh',i,len(l), ind, txt, '\n')
            
            if len(txt): 
                text = '\n'.join(txt)
                if MAX_CH < cnt:
                    if not ifTransPeriod: text = transPeriod(text)
                    elif not ifTransSemicolon: text = transSemicolon(text)
                    else: text = transCommaEtc(text)
                else:
                    text = trans(text)

                if text is not None:
                    for x, y in zip(ind, text.split('\n')): l[x] = y

                ind, txt, cnt = [], [], 0
        
        if i == len(l): break
        ind += [i]
        txt += [l[i]]
        cnt += len(l[i]) + 1
    return '\n'.join(l)







perSep = '\n'#'\n^!^\n'
def transPeriod (s):
    '''
    当句子太长时，分割句号进行翻译
    '''
    return toEnglish(s.replace('。', '。' + perSep).replace('.', '.' + perSep), True).replace(perSep, '')






semSep = '\n'#'\n^!!^\n'
def transSemicolon (s):
    '''
    当句子太长时，分割到分号进行翻译
    '''
    return toEnglish(s.replace('；', '；' + semSep).replace(';', ';' + semSep), True, True).replace(semSep, '')








commaEtcSep = '\n'
def transCommaEtc (s):
    '''
    当句子太长时，分割到逗号等级别进行翻译
    目前包括全角半角逗号、全角半角冒号、空格、顿号
    '''
    commaEtc = [',', '，', ':', '：', ' ', '、']
    for x in commaEtc: s = s.replace(x, x + commaEtcSep)
    rst = ''
    l = s.split(commaEtcSep)
    txt = ''
    for i in range(len(l) + 1):
        if i == len(l) or MAX_CH < len(txt) + len(l[i]) + 1:
            if len(txt):
                text = txt
                if MAX_CH < len(txt): log[-1](text)
                else: text = trans(text)
                if rst: rst += ' '
                rst += text
                txt = ''
        if i == len(l): break
        txt += l[i]
    return rst














