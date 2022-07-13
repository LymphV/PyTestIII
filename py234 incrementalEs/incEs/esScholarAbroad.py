'''

建立国外学者索引

------------

esProject : 建立国外学者索引
'''

this = '国外学者'
thisEn = 'scholar_abroad'


from .tmpIncTable.tmpScholarsAbroad import TmpScholarsAbroad as TmpScholars
from .tmpIncTable.tmpScholarsAbroad import table, idCol

from .esScholar import EsScholar

index = f'landinn_{thisEn}'
indexHl = f'landinn_{thisEn}_highlight'


esScholar = EsScholar(this, thisEn, table, idCol, index, indexHl, TmpScholars, True)
