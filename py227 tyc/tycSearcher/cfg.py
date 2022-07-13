'''

配置文件
包括

    token : 天眼查api token
    savePath : 原始json存储位置，None或空串为不存储
    updateGap : 调用接口内容失效的间隔（秒）
    updateGapEnterprise : 更新已有数据（企业）的最小间隔（秒）
    updateGapKeyword : 更新已有数据（关键词）的最小间隔（秒）
    maxPage : 调用api的最大页数（0或负数为全部翻页）
    maxSearchPage : 调用检索api的最大页数（0或负数为全部翻页）
    apiGap : 连续两次api调用的最小时间间隔（秒）
    
    nMaxKeywords : 单次更新最大关键词数
    nMaxFail : 一个关键词调用接口最大失败次数
    
    ifTeamMember : 是否使用TeamMember API
    ifProduct : 是否使用Product API
    ifTrademark : 是否使用Trademark API
    ifPatent : 是否使用Patent API
    ifSoftwareCopyright : 是否使用SoftwareCopyright API
    ifWebsite : 是否使用Website API
    ifSearch : 是否使用search API
    ifTrademarkSearch : 是否使用trademarkSearch API
    ifPatentSearch : 是否使用patentSearch API
    
    mysqlDb : mysql配置
'''



###天眼查api token
token = 'c5c3cc75-469f-4e59-9d14-c9ebc142dd9a'

###原始json存储位置，None或空串为不存储
savePath = '/LymphV/data/tyc/apiData' #None#


mins = 60
hours = 60 * mins
days = 24 * hours
months = 30 * days

###调用接口内容失效的间隔（秒）
updateGap = 3 * months

###更新已有数据（企业）的最小间隔（秒）（90天）
updateGapEnterprise = 3 * months

###更新已有数据（关键词）的最小间隔（秒）（90天）
updateGapKeyword = 3 * months

###调用api的最大页数（0或负数为全部翻页）
maxPage = 1 #2 #

###调用检索api的最大页数（0或负数为全部翻页）
maxSearchPage = 1 #2 #

###连续两次api调用的最小时间间隔（秒）
apiGap = 0.5


###单次更新最大关键词数
nMaxKeywords = 10

###一个关键词调用接口最大失败次数
nMaxFail = 10

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
mysqlDb = 'tianyancha'
