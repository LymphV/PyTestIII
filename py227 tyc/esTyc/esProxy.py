

from elasticsearch import Elasticsearch
from elasticsearch import TransportError, ConnectionError, ConnectionTimeout
from elasticsearch import helpers
import pymysql
import pandas as pd

if '.' in __name__:
    from .cfg import esHost, esPort
    from .utils import ourError
else:
    from cfg import esHost, esPort
    from utils import ourError

class EsProxy:
    '''
    es代理
    '''
    def __init__ (this):
        '''
        es代理
        '''
        this.__es = None
        this.start()

    @property
    def es (this):
        '''
        es的getter函数

        若无效或失去连接将自动重新连接
        '''
        if this.__es is None:
            this.restart()
        else:
            try:
                this.__es.info()
            except Exception as e:
                this.restart()
        return this.__es

    def start (this):
        '连接es'
        this.__es = Elasticsearch(hosts=esHost,port=esPort,timeout=60)

    def close (this):
        '关闭es'
        if this.__es: this.__es.close()
        this.__es = None

    def restart (this):
        '''
        重新连接

        没有找到Elasticsearch类有重新连接功能的函数，超时中断时只能重新生成一个对象
        '''
        this.close()
        this.start()

    def bulk (this, actions, errorInfo=None):
        '批量执行'
        while 1:
            try:
                rst = helpers.bulk(client=this.es,actions=actions)
                break
            except TransportError as e:
                if errorInfo is not None:
                    ourError(repr(e), errorInfo)
        return rst

    def delete_by_query(this, *x, **y):
        '删除检索到的行'
        return this.es.delete_by_query(*x, **y)
