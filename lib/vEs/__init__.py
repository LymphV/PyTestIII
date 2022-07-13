

from elasticsearch import Elasticsearch
from elasticsearch import TransportError, ConnectionError, ConnectionTimeout
from elasticsearch import helpers
import pandas as pd
import json

from vUtil.vLog import vError

from .cfg import esHost, esPort

class EsProxy:
    '''
    es代理
    '''

    __version__ = 20211207
    __author__ = 'LymphV@163.com'

    def __init__ (this, host=esHost, port=esPort):
        '''
        es代理
        '''
        this.__es = None
        this.host = host
        this.port = port
        this.start()

    def __str__ (this):
        data = {'host' : this.host, 'port' : this.port}
        return f'<vMysql.EsProxy({data})>'
    
    def __repr__ (this):
        return str(this)
    
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
        this.__es = Elasticsearch(hosts=this.host,port=this.port,timeout=300)

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
            except ConnectionTimeout as e:
                if errorInfo is not None:
                    ourError(errorInfo, repr(e))
        return rst
    
    def createIndex (this, index, file=None, body=None):
        '''
        创建索引
        
        index : 索引名
        file : body文件名，默认为f'{index}.json'
        body : body字典，默认为file的内容
        '''
        if body is None:
            with open(file or f'{index}.json') as f:
                body = json.load(f)
        return this.indices.create(index, body)
    
    def dropIndex (this, index):
        '删除索引'
        return this.indices.delete(index)
        
    def reindex (this, indexFrom, indexTo):
        '拷贝索引'
        body = {
            "source": {
                "index": indexFrom
            },
            "dest": {
                "index": indexTo
            }
        }
        return this.es.reindex(body)
    
    def __getattr__ (this, name):
        return this.es.__getattribute__(name)