'''

配置文件
包括
    userAgent : 翻译所使用的浏览器的userAgent
    home : 主页
    tqdmNcols : tqdm使用的宽度
    waitUnit : 加载最少等待时间
    waitLoading : 加载最长等待时间（不含waitUnit）
    scholarGap : 连续两次学者页的最小间隔
    mysqlIp : mysql配置
    mysqlPort : mysql配置
    mysqlDb : mysql配置
    mysqlUser : mysql配置
    mysqlPassword : mysql配置
'''

if '.' in __name__:
    from .utils import typeOfScript
else:
    from utils import typeOfScript

###要使用所使用的浏览器的userAgent
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"

###Aminer专家库主页
home = 'https://gct.aminer.cn/'


###tqdm使用的宽度
tqdmNcols = None if typeOfScript() == 'jupyter' else 80


###加载最少等待时间
waitUnit = 2


###加载最长等待时间（不含waitUnit）
waitLoading = 10

###连续两次学者页的最小间隔
scholarGap = 20


###mysql配置
mysqlIp = '10.208.63.47'
mysqlPort = 3306
mysqlDb = 'AminerClimbed'
mysqlUser = 'root'
mysqlPassword = 'linlei'
