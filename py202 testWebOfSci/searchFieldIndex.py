'''

提供wos检索界面的search field序号

'''


class SearchFieldIndex:
    '''
    search field用序号
    语种和文献类型输入方式不同，暂不可用
    ------------------
    TS : 主题
    TI : 标题
    AU : 作者
    SO : 出版物名称
    PY : 出版年
    FO : 资金机构
    OG : 机构扩展
    AL : 所有字段
    
    UT : 入藏号
    AD : 地址
    AI : 作者识别号
    CF : 会议
    DT : 文献类型
    DO : DOI
    ED : 编者
    FG : 授权号
    GP : 团体作者
    LA : 语种
    PM : PubMed ID
    '''
    
    TS = 0
    TI = 1
    AU = 2
    SO = 3
    PY = 4
    FO = 5
    OG = 6
    AL = 7
    
    UT = -11
    AD = -10
    AI = -9
    CF = -8
    DT = -7
    DO = -6
    ED = -5
    FG = -4
    GP = -3
    LA = -2
    PM = -1





###str到SearchFieldIndex的映射
str2SearchFieldIndex = {
    'TS' : SearchFieldIndex.TS,
    'TI' : SearchFieldIndex.TI,
    'AU' : SearchFieldIndex.AU,
    'SO' : SearchFieldIndex.SO,
    'PY' : SearchFieldIndex.PY,
    'FO' : SearchFieldIndex.FO,
    'OG' : SearchFieldIndex.OG,
    'AL' : SearchFieldIndex.AL,
    'UT' : SearchFieldIndex.UT,
    'AD' : SearchFieldIndex.AD,
    'AI' : SearchFieldIndex.AI,
    'CF' : SearchFieldIndex.CF,
    'DT' : SearchFieldIndex.DT,
    'DO' : SearchFieldIndex.DO,
    'ED' : SearchFieldIndex.ED,
    'FG' : SearchFieldIndex.FG,
    'GP' : SearchFieldIndex.GP,
    'LA' : SearchFieldIndex.LA,
    'PM' : SearchFieldIndex.PM,
}

###默认search field
dft = 'TI'
SearchFieldIndex.dft = str2SearchFieldIndex[dft]