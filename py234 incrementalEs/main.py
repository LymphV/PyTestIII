

import click
from time import time, sleep

if '.' in __name__:
    from .timeManager import TimeManagerFile, TimeManagerMysql, TimeManager
    from .incEs import esPaper, esProject, esScholar, esScholarAbroad
    from .incEs import esPatent, esProduct, esSoftwareCopyright, esEnterprise
    from .utils import setTimeManager, ourLog, ourError, frmt
    from .cfg import updateGap
else:
    from timeManager import TimeManagerFile, TimeManagerMysql, TimeManager
    from incEs import esPaper, esProject, esScholar, esScholarAbroad
    from incEs import esPatent, esProduct, esSoftwareCopyright, esEnterprise
    from utils import setTimeManager, ourLog, ourError, frmt
    from cfg import updateGap

from vUtil.vTqdm import tqdm, trange

__version__ = 20210830
__author__ = 'LymphV@163.com'


choices = ['file', 'mysql', 'all']
help = f'choose a time manager from {choices}'
choices = click.Choice(choices, case_sensitive=False)

@click.command()
@click.option('-t', prompt='time manager', type=choices, help=help)
def main(t):
    setTimeManager(t)

    Tm = {
        'file' : TimeManagerFile,
        'mysql' : TimeManagerMysql,
        'all' : TimeManager,
    }[t]

    if t == 'all':
        allChoice = getAllChoice()
        if allChoice != 'all':
            return esAll(Tm, allChoice)

    iRound = 0
    while 1:
        tStart = time()
        tm = Tm()

        if tm.check():
            iRound = 0
            tm.start()

            ourLog(f'({t})更新[{tm.last},{tm.now})')
            frmt(f'({t})更新[{tm.last},{tm.now})')

            esPatent(tm.last, tm.now)
            esProduct(tm.last, tm.now)
            esSoftwareCopyright(tm.last, tm.now)
            esEnterprise(tm.last, tm.now)

            esProject(tm.last, tm.now)
            esPaper(tm.last, tm.now)
            esScholar(tm.last, tm.now)
            esScholarAbroad(tm.last, tm.now)

            tm.close()

            print ('-' * 80)

            if t == 'all': break

        tEnd = time()
        if tEnd < tStart + updateGap:
            iRound += 1
            with trange(int(tStart + updateGap - tEnd), leave=False) as tr:
                for i in tr:
                    frmt(f'等待下轮{iRound}', tqdm=tr)
                    sleep(1)

allChoices = {
    'patent' : esPatent,
    'product' : esProduct,
    'softwarecopyright' : esSoftwareCopyright,
    'enterprise' : esEnterprise,
    'project' : esProject,
    'paper' : esPaper,
    'scholar' : esScholar,
    'scholarabroad' : esScholarAbroad,
}

def getAllChoice ():
    while  1:
        rst = input(f'''es which{(*allChoices, 'all')}: ''').strip().lower()
        if rst == 'all' or rst in allChoices: break
    return rst

def esAll (Tm, allChoice):
    esSth = allChoices[allChoice]

    tm = Tm()
    tm.start()

    ourLog(f'(all)更新{allChoice}[{tm.last},{tm.now})')
    frmt(f'(all)更新{allChoice}[{tm.last},{tm.now})')
    esSth(tm.last, tm.now)

    tm.close()

    print ('-' * 80)



if __name__ == '__main__':
    main()
