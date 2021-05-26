'''
AminerPeterait

根据name中的名字检索学者，并采集学者信息存入数据库中
'''

import base64
from time import sleep, time
import pymysql
from pymysql import err
import click

if __name__ == '__main__':
    from driverOps import getDriver, waitTillOpen, waitTillLoaded, closeAllOther
    from AminerScholarExtracter import AminerScholarExtracter
    from AminerSearchExtracter import searchName, getScholarPage, getScholarIds
    from utils import stdAminerId, typeOfScript, frmt
    from driverUtils import getTextByXpath, getTextsByXpath, getAttributeByXpath, getTextById
    from cfg import tqdmNcols as ncols, mysqlIp, mysqlPort, mysqlUser, mysqlPassword, mysqlDb, waitUnit, waitLoading, scholarGap
    from MysqlInserter import addCursor, checkScholar, checkDoneName, insertScholar, insertDoneName
    from MysqlInserter import insertAwards, insertPortrait, insertTalentPools, insertWebpages, insertPapers, insertPublish
    from namelist import names as namelist
else:
    from .driverOps import getDriver, waitTillOpen, waitTillLoaded, closeAllOther
    from .AminerScholarExtracter import AminerScholarExtracter
    from .AminerSearchExtracter import searchName, getScholarPage, getScholarIds
    from .utils import stdAminerId, typeOfScript, frmt
    from .driverUtils import getTextByXpath, getTextsByXpath, getAttributeByXpath, getTextById
    from .cfg import tqdmNcols as ncols, mysqlIp, mysqlPort, mysqlUser, mysqlPassword, mysqlDb, waitUnit, waitLoading, scholarGap
    from .MysqlInserter import addCursor, checkScholar, checkDoneName, insertScholar, insertDoneName
    from .MysqlInserter import insertAwards, insertPortrait, insertTalentPools, insertWebpages, insertPapers, insertPublish
    from .namelist import names as namelist


from vUtil.vFile import fprint
from vUtil.vEmail import sendEmail
from vUtil.vTime import getNow, convertSeconds

if typeOfScript() == 'jupyter':
    from tqdm.notebook import tqdm, trange
else:
    from tqdm import tqdm, trange

def ourError (name, error, errorType = ''):
    fprint(f'[ERROR] ({getNow()}) {repr(name)} : {errorType} : {repr(error)}\n', file='error.txt', path='error')

def ourLog (name, log, logType = ''):
    fprint(f'[LOG] ({getNow()}) {repr(name)} : {logType} : {repr(log)}\n', file='log.txt', path='log')


def __main (whoami, start):
    ### 打开浏览器
    driver = getDriver()
    
    frmt('打开浏览器')
    ourLog('','打开浏览器')

    ### 连接数据库

    db = pymysql.connect(mysqlIp, mysqlUser, mysqlPassword,port=mysqlPort,charset='utf8',db=mysqlDb)
    cursor = db.cursor()
    addCursor(cursor)
    frmt('连接数据库')
    ourLog('','连接数据库')

    try:
        ### 采集
        now = 0
        frmt('检验人名')
        names = [name for name in tqdm(namelist, ncols=ncols) if not checkDoneName(name)]
        frmt('开始采集')
        ourLog('','开始采集')
        for name in tqdm(names, ncols=ncols):
            frmt(name,end=' ')
            ourLog(name,'')
            waitTime = waitUnit
            iWait = 0
            ###获取id
            while 1:
                if not searchName(driver, name):
                    sleep(waitTime)
                    iWait += 1
                    if waitTime < 2 * waitLoading: waitTime += waitUnit
                    else: ourError(name, iWait, 'list open failed')
                    continue
                waitTime = waitUnit
                ids = getScholarIds(driver, name)
                if ids is not None: break
                iWait += 1
            
            ids = [id for id in set(ids) if not checkScholar(id)]
            ###采集学者信息
            for id in tqdm(ids, ncols=ncols, leave=False):
                frmt(name, id, end=' ')
                ourLog(name,id)
                waitTime = waitUnit
                iWait = 0
                noNameCount = 0
                
                while time() < now + scholarGap: sleep(1)
                now = time()
                while 1:
                    try:
                        getScholarPage(driver, id)
                        ex = AminerScholarExtracter(driver)

                        nowName, pinyin = ex.getName()
                        portrait = ex.getPortrait()
                        title = ex.getTitle()
                        department = ex.getDepartment()
                        email = ex.getEmail()
                        phone = ex.getPhone()
                        fax = ex.getFax()
                        address = ex.getAddress()
                        webpages = ex.getWebPages()
                        awards = ex.getAwards()
                        talentPools = ex.getTalentPools()
                        experience = ex.getExperience()
                        education = ex.getEducation()
                        brief = ex.getBrief()
                        papers = ex.getPapers()
                    except KeyboardInterrupt as e:
                        raise e
                    except Exception as e:
                        sleep(waitTime)
                        iWait += 1
                        if waitTime < 2 * waitLoading: waitTime += waitUnit
                        ourError(name, f'id({id}) wait({iWait})', str(e))
                        continue
                        #if str(e) == 'load failed' or str(e) == 'no sort by reference':
                        #    continue
                        #raise e
                    if nowName is None or nowName != name:
                        if noNameCount < 10:
                            iWait += 1
                            noNameCount += 1
                            ourError(name, f'id({id}) wait({iWait})', f'no name `{nowName}`')
                            continue
                        else: 
                            ourError(name, f'id({id}) wait({iWait})', f'invalid id without name `{nowName}`')
                            break
                    ourLog(name, 'info done', id)
                    
                    insertScholar(id, name, pinyin, phone, title, department, fax, email, address, experience, education, brief)
                    insertPortrait(id, portrait)
                    insertWebpages(id, webpages)
                    insertAwards(id, awards)
                    insertTalentPools(id, talentPools)
                    insertPapers(papers)
                    insertPublish(id, papers)
                    db.commit()
                    closeAllOther(driver)
                    break
            insertDoneName(name)
            db.commit()
        frmt('采集完成')
        ourLog('','采集完成')
    finally:
        ### 关闭数据库
        db.close()
        frmt('关闭数据库')
        ourLog('','关闭数据库')

        ### 关闭浏览器
        driver.quit()
        frmt('关闭浏览器')
        ourLog('','关闭浏览器')
        
    ###发送邮件
    sendEmail(f'Sir, scholars\' information downloaded, which cost {convertSeconds(time() - start)}.', f'mission accomplished reported by spider `{whoami}`')
    frmt('发送邮件')
    ourLog('','发送邮件')

@click.command()
@click.option('-I', '--whoami', 'whoami', prompt='who am i? please name me', help='the name of me, the spider ready to climb')
def main (whoami):
    start = time()
    while 1:
        try:
            __main(whoami, start)
            break
        except KeyboardInterrupt as e:
            raise e
        except err.OperationalError as e:
            ourError('', str(e), 'err.OperationalError')
        except Exception as e:
            ourError('', str(e), 'Exception')

if __name__ == '__main__':
    main()
    


    