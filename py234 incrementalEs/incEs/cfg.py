'''

配置文件
包括
    nIdSep : 同企业/学者合并不同字段时的分隔符数

    mysqlDb : mysql配置

'''

### 同企业/学者合并不同字段时的分隔符数，防止es match_phrase时将短语分开匹配进多行中
### match_phrase的slop为10，分隔符数暂设为12
nIdSep = 12

###mysql配置
mysqlDb = 'landinn'
