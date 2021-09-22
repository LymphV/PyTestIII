'''

配置文件
包括
    esHost : es配置
    esPort : es配置
    esMaster : es配置

'''

###es配置
# esHost = '10.208.63.46'
esHost = '172.17.184.30'
esPort = 9200
esMaster = f'http://{esHost}:{esPort}'