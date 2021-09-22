#!/usr/bin/env python
# coding: utf-8
'''
    isValid():验证图片url是否有效
        e.g:
            'hhtp://123.html' --> False  'http://XXX/self/img/XXX.jpg' --> True
        Args:
            string 图片url
        Return:
            string 分辨率最大的图片对应的url 
    --------------------------------------------------------------------
    largePic():获取分辨率最大的图片
        e.g:
            {"pic1":'http://XXX/self/img/XXX.jpg_10*10',"pic2":'http://XXX/self/img/XXX.jpg200*200'} --> 'http://XXX/self/img/XXX.jpg200*200'
        Args:
            dict 需要对比的图片及其url e.g:{"pic1":url1,"pic2":url2}
        Return:
            string 分辨率最大的图片对应的url
'''
__version__ = 1.1
__author__ = 'esue_yan@163.com'
    
from urllib import request
from PIL import Image
import ssl
 
def isValid(url):
    '''
    验证图片url是否有效
    '''
    try:
        request.urlopen(url)
        Image.open(request.urlopen(url))
        return True
    except Exception as e:
        return False

def largePic(pic):
    '''
    获取分辨率最大的图片
    '''
    pic_size = {}
    for key,value in pic.items():
        if value:
            width = Image.open(request.urlopen(value)).width
            height = Image.open(request.urlopen(value)).height
        else:
            width,height = 0,0
        pic_size[width*height]=value
    if max(pic_size.keys()) == 0 : return None
    return pic_size[max(pic_size.keys())]    