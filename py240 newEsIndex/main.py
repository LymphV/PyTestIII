'''
更新索引
新建索引删除旧索引

json文件名为检索索引名（别名）+'.json'
新建索引为检索索引名（别名）+日期
索引数据导入完成后，删除所有旧索引，并为新索引建立别名
'''


import click, os
from time import time, sleep


from service_incEs.timeManager import TimeManager
from service_incEs.utils import setTimeManager

if '.' in __name__:
    from .esNew import getEsNew
else:
    from esNew import getEsNew
    

from vUtil.vLog import frmt, vError, vLog
from vUtil.vTqdm import tqdm, trange
from vEs import EsProxy

__version__ = 20220620
__author__ = 'LymphV@163.com'


choices = [    
    'patent',
    'product',
    'softwarecopyright',
    'enterprise',
    'project',
    'paper',
    'scholar',
    'scholarabroad'
]
help = f'choose a index from {choices}'
choices = click.Choice(choices, case_sensitive=False)

@click.command()
@click.option('-i', prompt='index', type=choices, help=help)
def main(i):
    setTimeManager('all')

    esNew, *inds = getEsNew(i)

    tm = TimeManager()
    tm.start()

    frmt(*vLog(f'new更新{i}'))
    es = EsProxy()
    
    frmt(*vLog(f'索引创建'))
    with tqdm(inds) as tinds:
        for indexNew, index in tinds: ### 新索引名（有时间后缀）和使用的索引名（别名，无后缀）
            frmt('创建', indexNew, tqdm=tinds)
            es.createIndex(indexNew, file=f'{index}.json')
    es.close()
    
    frmt(*vLog(f'索引更新'))
    esNew(tm.last, tm.now)
    tm.close()
    
    
    with tqdm(inds) as tinds:
        frmt(*vLog(f'索引迁移'), tqdm=tinds)
        for indexNew, index in tinds:
            try:
                indexesOld = [*es.indices.get_alias(index)] ### 旧索引，如果旧版本未使用别名则无后缀，如果是新版本则有后缀
            except: ### 无旧索引
                indexesOld = []
            frmt(*vLog('索引迁移', f'{indexesOld}->{indexNew}'), tqdm=tinds)
            
            ### 删除old索引，新索引加别名
            es.indices.update_aliases({
                "actions": [
                    {"add": {"index": indexNew, "alias": index}},
                    *[{"remove_index":{"index":x}} for x in indexesOld]
                ]
            })
    es.close()

    print ('-' * 80)


if __name__ == '__main__':
    main()
