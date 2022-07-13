'''
天眼查数据更新

从数据库中获取关键词，
调用天眼查接口更新数据并存入tianyancha数据库，
将更新的增量tianyancha数据融入landinn数据库，
将更新的landinn数据索引入es

------

main : 天眼查数据更新主程序
'''


from .main import main

__version__ = 20210506
__author__ = 'LymphV@163.com'