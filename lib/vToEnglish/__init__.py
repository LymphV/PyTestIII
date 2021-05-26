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

isEnglish(s:str)->bool 是否为纯英文
hasChinese(word:str)->bool 是否含有中文
countChinese(word:str)->int 中文个数
'''

from .detect import isEnglish, hasChinese, countChinese
from .translate import translate
from .toEnglish import toEnglish, setIfPrint, setAutoReset, getIRetry, resetIRetry, addLog


__version__ = 20201110
__author__ = 'LymphV@163.com'
