'''

绘制工具
将图片或浏览器转为可在jupyter notebook中直接显示的Image类型

========

drawPng : 绘制图片
draw : 绘制浏览器界面

'''


from PIL import Image
from io import StringIO,BytesIO

def drawPng (png):
    '''
    绘制图片
    
    Parameters
    ----------
    png : byte串png
    
    Returns
    -------
    drawPng : png转为的Image对象
    '''
    return Image.open(BytesIO(png))
    
def draw (dv):
    '''
    绘制浏览器界面
    
    Parameters
    ----------
    dv : webdriver
    
    Returns
    -------
    draw : 浏览器转为的Image对象
    '''
    return drawPng(dv.get_screenshot_as_png())
