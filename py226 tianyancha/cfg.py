'''

配置文件
包括

    token : 天眼查api token
    savePath : 原始json存储位置，None或空串为不存储
    tqdmNcols : tqdm使用的宽度
    updateGap : 更新已有数据的最小间隔（秒）
    maxPage : 调用api的最大页数（0或负数为全部翻页）
    apiGap : 连续两次api调用的最小时间间隔（秒）
    
    ifTeamMember : 是否使用TeamMember API
    ifProduct : 是否使用Product API
    ifTrademark : 是否使用Trademark API
    ifPatent : 是否使用Patent API
    ifSoftwareCopyright : 是否使用SoftwareCopyright API
    ifWebsite : 是否使用Website API
    ifSearch : 是否使用search API
    ifTrademarkSearch : 是否使用trademarkSearch API
    ifPatentSearch : 是否使用patentSearch API
    
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



###天眼查api token
token = 'c5c3cc75-469f-4e59-9d14-c9ebc142dd9a'

###原始json存储位置，None或空串为不存储
savePath = 'apiData' #None

###tqdm使用的宽度
tqdmNcols = None if typeOfScript() == 'jupyter' else 80

###更新已有数据的最小间隔（秒）（90天）
updateGap = 60 * 60 * 24 * 30 * 3

###调用api的最大页数（0或负数为全部翻页）
maxPage = 1 #2 #

###连续两次api调用的最小时间间隔（秒）
apiGap = 0.5

###是否使用各api
ifTeamMember = True
ifProduct = True
ifTrademark = False
ifPatent = True
ifSoftwareCopyright = True
ifWebsite = False
ifSearch = False
ifTrademarkSearch = False
ifPatentSearch = True

###mysql配置
mysqlIp = '10.208.63.47'
mysqlPort = 3306
mysqlDb = 'tianyancha'
mysqlUser = 'root'
mysqlPassword = 'linlei'
