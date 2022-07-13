
from time import time

if __name__ == '__main__': 
    from updateKeyword import UpdateKeyword
    from mysqlInserter import db
    from utils import ourError, ourLog, frmt
    from countManager import CountManager
    from keywords import keywords
else:
    from .updateKeyword import UpdateKeyword
    from .mysqlInserter import db 
    from .utils import ourError, ourLog, frmt
    from .countManager import CountManager
    from .keywords import keywords


from vUtil.vEmail import sendEmail
from vUtil.vTime import convertSeconds
from vUtil.vTqdm import tqdm, trange

__version__ = 20210830
__author__ = 'LymphV@163.com'

def main (keywords=keywords):
    start = time()
    db.close() ### MysqlProxy有自启动功能
    
    apiCount = {}
    
    try:
        with tqdm(keywords) as tq:
            for keyword in tq:
                frmt(f'{repr(keyword)}', tqdm=tq)
                
                if keyword in apiCount: continue
                
                apiCount[keyword] = CountManager.initCount()
                try:
                    uk = UpdateKeyword(keyword)
                    uk.update(cnt=apiCount, tq=tq)
                finally:
                    cnt = apiCount[keyword]
                    cm = CountManager()
                    cm.add(keyword, cnt)
                    cm.close()
    except KeyboardInterrupt as e:
        ###发送邮件
        sendEmail(f'Tianyancha information download error.Error:{repr(e)}', f'tyc search failed')
        frmt('发送邮件', start='\n')
        ourError(repr(e))
        ourLog('发送错误邮件')
        raise e
    finally:
        frmt ('api调用次数', f'关键词({apiCount}) 总计({sum(apiCount.values())}) 耗时({convertSeconds(time() - start)})')
        ourLog ('api调用次数', f'关键词({apiCount}) 总计({sum(apiCount.values())}) 耗时({convertSeconds(time() - start)})')
    
        ### 关闭数据库
        db.close()
        frmt('关闭数据库', start='\n')
        ourLog('关闭数据库')


if __name__ == '__main__':
    main()