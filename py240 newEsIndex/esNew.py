
from vUtil.vTime import getToday

def getEsNew (option):
    '''
    Returns
    -------
    esXXX : 可执行对象，用于更新索引
    *[新索引,使用的索引别名] : 若干返回值，每个返回值为[新索引,使用的索引别名]对，
        新索引为新创建的索引，
        使用的索引别名为检索使用的索引别名，之前为索引，以后为别名
        需要删除该别名原有索引，并将新索引重命名为替换索引，并删除新索引
    '''
    options = {
        'patent' : getEsPatentNew,
        'product' : getEsProductNew,
        'softwarecopyright' : getEsSoftwareCopyrightNew,
        'enterprise' : getEsEnterpriseNew,
        'project' : getEsProjectNew,
        'paper' : getEsPaperNew,
        'scholar' : getEsScholarNew,
        'scholarabroad' : getEsScholarAbroadNew,
    }
    return options[option]()
    


def toNew (index):
    return index + f'_{getToday()}'

### 返回为(esXXX, *[新索引,替换索引])


def getEsPatentNew ():
    from service_incEs.incEs.esPatent import EsPatent, this, thisEn, table, idCol, index, TmpPatents
    
    indexNew = toNew(index)
    return EsPatent(this, thisEn, table, idCol, indexNew, TmpPatents), [indexNew, index]

def getEsProductNew ():
    from service_incEs.incEs.esProduct import EsProduct, this, thisEn, table, idCol, index, TmpProducts
    
    indexNew = toNew(index)
    return EsProduct(this, thisEn, table, idCol, indexNew, TmpProducts), [indexNew, index]

def getEsSoftwareCopyrightNew ():
    from service_incEs.incEs.esSoftwareCopyright import EsSoftwareCopyright, this, thisEn, table, idCol, index, TmpSoftwareCopyrights
    
    indexNew = toNew(index)
    return EsSoftwareCopyright(this, thisEn, table, idCol, indexNew, TmpSoftwareCopyrights), [indexNew, index]

def getEsEnterpriseNew ():
    from service_incEs.incEs.esEnterprise import EsEnterprise, this, thisEn, table, idCol, index, indexHl, TmpEnterprises
    
    indexNew = toNew(index)
    indexHlNew = toNew(indexHl)
    return EsEnterprise(this, thisEn, table, idCol, indexNew, indexHlNew, TmpEnterprises), [indexNew, index], [indexHlNew, indexHl]

def getEsProjectNew ():
    from service_incEs.incEs.esProject import EsProject, this, thisEn, table, idCol, index, TmpProjects
    
    indexNew = toNew(index)
    return EsProject(this, thisEn, table, idCol, indexNew, TmpProjects), [indexNew, index]
def getEsPaperNew ():
    from service_incEs.incEs.esPaper import EsPaper, this, thisEn, table, idCol, index, TmpPapers
    
    indexNew = toNew(index)
    return EsPaper(this, thisEn, table, idCol, indexNew, TmpPapers), [indexNew, index]

def getEsScholarNew ():
    from service_incEs.incEs.esScholar import EsScholar, this, thisEn, table, idCol, index, indexHl, TmpScholars
    
    indexNew = toNew(index)
    indexHlNew = toNew(indexHl)
    return EsScholar(this, thisEn, table, idCol, indexNew, indexHlNew, TmpScholars), [indexNew, index], [indexHlNew, indexHl]

def getEsScholarAbroadNew ():
    from service_incEs.incEs.esScholarAbroad import EsScholar, this, thisEn, table, idCol, index, indexHl, TmpScholars
    
    indexNew = toNew(index)
    indexHlNew = toNew(indexHl)
    return EsScholar(this, thisEn, table, idCol, indexNew, indexHlNew, TmpScholars, True), [indexNew, index], [indexHlNew, indexHl]

