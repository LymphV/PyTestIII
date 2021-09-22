'''

有道翻译同义词
youdaoSynonym

=============
提供：
    1.生成中文短语的英文同义词集
    
>>>yd = YoudaoSynonym() ###打开浏览器，打开有道翻译网页
>>>yd.getSynonyms('光学计算') ###生成同义词集
{'Optical computing', 'optical calculation', 'optical computing'}
>>>yd.close() ###关闭浏览器
'''

from .youdaoSynonym import YoudaoSynonym



__version__ = 20210618
__author__ = 'LymphV@163.com'