'''

配置文件
包括
    
    codeErr : 不可重复尝试的sql语句错误类型
    maxErr : 最大连续sql语句错误次数

'''


codeErr = {
    1406, ### Data too long for column
    1064, ### have an error in your SQL syntax
    1054, ### Unknown column
    1062, ### Duplicate entry
    1146, ### Table doesn't exist
    1049, ### Unknown database
    1436, ### Thread stack overrun
    1241, ### Operand should contain x column(s)
    1248, ### Every derived table must have its own alias
    1364, ### Field doesn't have a default value
}

maxErr = 100