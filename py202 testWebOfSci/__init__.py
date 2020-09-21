'''

wospidey
========
提供：
    1.以wos核心合集为数据库，按指定时间跨度的关键词检索
    2.以日期降序、被引频次降序、相关性等排序方式排序检索结果
    3.从检索结果中抽取文章的标题、作者、通讯作者、电子邮箱等字段



'''

from . import cfg
from . import driverOps
from . import searcher
from . import listExtracter
from . import paperExtracter

from . import wospidey
from . import main

__version__ = 20200921
__author__ = 'LymphV@163.com'