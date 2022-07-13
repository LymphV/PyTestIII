'''

配置文件
包括


    mysqlIp : mysql配置
    mysqlPort : mysql配置
    mysqlDb : mysql配置
    mysqlUser : mysql配置
    mysqlPassword : mysql配置

    esHost : es配置
    esPort : es配置
    esMaster : es配置

'''



###mysql配置
mysqlIp = '10.208.63.47'
mysqlPort = 3306
mysqlDb = 'landinn'
mysqlUser = 'root'
mysqlPassword = 'linlei'

###es配置
esHost = '10.208.63.46'#'es00'#
esPort = 9200
esMaster = f'http://{esHost}:{esPort}'
