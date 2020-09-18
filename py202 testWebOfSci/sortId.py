'''

提供wos检索结果界面的排序id

'''

class SortId:
    '''
    排序用id
    仅提供wos用户界面提供的，如有需要可以自由搭配
    --------
    PYD : 日期降序
    PYA : 日期升序
    LCD : 被引频次降序
    LCA : 被引频次升序
    ACA : 使用次数（2013 年至今）
    RSD : 相关性
    LDD : 最近添加
    AC180D : 使用次数（最近180天）
    AUA : 第一作者升序
    AUD : 第一作者降序
    SOA : 来源出版物标题升序
    SOD : 来源出版物标题降序
    CFA : 会议名称升序
    CFD : 会议名称降序
    '''
    PYD = 'PY.D;LD.D;SO.A;VL.D;PG.A;AU.A' ###日期降序
    PYA = 'PY.A;LD.A;SO.A;VL.A;PG.A;AU.A' ###日期升序
    LCD = 'LC.D;PY.D;AU.A.en;SO.A.en;VL.D;PG.A' ###被引频次降序
    LCA = 'LC.A;PY.D;AU.A.en;SO.A.en;VL.D;PG.A' ###被引频次升序
    ACA = 'ACA.D;PY.D;LD.D;SO.A;VL.D;PG.A;AU.A' ###使用次数（2013 年至今）
    RSD = 'RS.D;PY.D;AU.A;SO.A;VL.D;PG.A' ###相关性
    LDD = 'LD.D;PY.D;SO.A;VL.D;PG.A;AU.A' ###最近添加
    AC180D = 'AC180.D;PY.D;LD.D;SO.A;VL.D;PG.A;AU.A' ###使用次数（最近180天）
    AUA = 'AU.A.en;PY.D;SO.A;VL.D;PG.A' ###第一作者升序
    AUD = 'AU.D.en;PY.D;SO.A;VL.D;PG.A' ###第一作者降序
    SOA = 'SO.A;PY.D;VL.D;AU.A;PG.A' ###来源出版物标题升序
    SOD = 'SO.D;PY.D;VL.D;AU.A;PG.A' ###来源出版物标题降序
    CFA = 'CF.A;PY.D;AU.A;SO.A;VL.D;PG.A' ###会议名称升序
    CFD = 'CF.D;PY.D;AU.A;SO.A;VL.D;PG.A' ###会议名称降序

###str到SortId的映射
str2SortId = {
    'PYD' : SortId.PYD,
    'PYA' : SortId.PYA,
    'LCD' : SortId.LCD,
    'LCA' : SortId.LCA,
    'ACA' : SortId.ACA,
    'RSD' : SortId.RSD,
    'LDD' : SortId.LDD,
    'AC180D' : SortId.AC180D,
    'AUA' : SortId.AUA,
    'AUD' : SortId.AUD,
    'SOA' : SortId.SOA,
    'SOD' : SortId.SOD,
    'CFA' : SortId.CFA,
    'CFD' : SortId.CFD,
}