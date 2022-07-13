
import pymysql
from time import time

if __name__ == '__main__': 
    from keywords import keywords
    from updateKeyword import UpdateKeyword
    from cfg import tqdmNcols as ncols, mysqlIp, mysqlPort, mysqlUser, mysqlPassword, mysqlDb
    from mysqlInserter import addCursor 
    from utils import ourError, ourLog, frmt, typeOfScript
else:
    from .keywords import keywords
    from .updateKeyword import UpdateKeyword
    from .cfg import tqdmNcols as ncols, mysqlIp, mysqlPort, mysqlUser, mysqlPassword, mysqlDb
    from .mysqlInserter import addCursor 
    from .utils import ourError, ourLog, frmt, typeOfScript


from vUtil.vEmail import sendEmail
from vUtil.vTime import getNow, convertSeconds

if typeOfScript() == 'jupyter':
    from tqdm.notebook import tqdm, trange
else:
    from tqdm import tqdm, trange

__version__ = 20210330
__author__ = 'LymphV@163.com'

def main ():
    start = time()
    ### 连接数据库

    db = pymysql.connect(mysqlIp, mysqlUser, mysqlPassword,port=mysqlPort,charset='utf8',db=mysqlDb)
    addCursor(db.cursor())
    frmt('连接数据库')
    ourLog('','连接数据库')
    
    apiCount = {}
    
    try:
        for keyword in tqdm(keywords, ncols=ncols):
            uk = UpdateKeyword(keyword)
            cnt = uk.update(db)
            apiCount[keyword] = apiCount.get(keyword, 0) + cnt
    except KeyboardInterrupt as e:
        ###发送邮件
        sendEmail(f'Sir, tianyancha information download error, which cost {convertSeconds(time() - start)}.', f'mission failed')
        frmt('发送邮件')
        ourLog('','发送邮件')
        raise e
    finally:
        frmt (f'关键词({apiCount}) 总计({sum(apiCount.values())})','api调用次数')
        ourLog ('', f'关键词({apiCount}) 总计({sum(apiCount.values())})','api调用次数')
    
        ### 关闭数据库
        db.close()
        frmt('\n关闭数据库')
        ourLog('','关闭数据库')

        
    ###发送邮件
    sendEmail(f'Sir, tianyancha information downloaded, which cost {convertSeconds(time() - start)}.', f'mission accomplished')
    frmt('发送邮件')
    ourLog('','发送邮件')

if __name__ == '__main__':
    main()