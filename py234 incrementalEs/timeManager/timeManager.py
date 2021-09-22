


class TimeManager:
    '''
    TimeManager

    -----------

    管理更新时间
    TimeManager.last : 上次更新时间
    TimeManager.now : 本次更新时间

    TimeManager.start : 启动，读取本次更新时间
    TimeManager.close : 关闭，保存本次更新时间
    '''

    __version__ = 20210615
    __author__ = 'LymphV@163.com'

    def __init__ (this, last=None, now=None):
        this.last = last
        this.now = now

    def __repr__ (this):
        rst = {'last' : this.last, 'now' : this.now}
        return f'< {this.__class__.__name__} {rst} >'

    def __str__ (this):
        return repr(this)

    def check (this):
        '''
        检测，是否有有效的当前时间
        '''
        return True

    def start (this):
        '''
        启动，读取本次更新时间
        '''

    def close (this):
        '''
        关闭，保存本次更新时间
        '''
