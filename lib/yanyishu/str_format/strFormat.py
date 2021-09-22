#!/usr/bin/env python
# coding: utf-8

import string
import pandas as pd
import re
from pymysql.converters import escape_string
from ch_conver import trd2smp,smp2trd

class strFormat:
    '''
    字符串标准化
    Args:
        element: 待处理字符串 
        choice: strip（默认值，去除首尾空格） allSpace（去除所有空格）
    Functions:
        check_contain_chinese(): 检查字符串是否为中英文 | return:bool True-中文 False-英文
        strQ2B(): 全角转换为半角 | return:string
        removeAllSpace():去掉所有空格 | return:string
        strStrip():去除首尾空格 | return:string
        standardization():字符串标准化，包括全角转半角+去空格，繁转简 | return:string
        mysql_format():mysql入库数据标准化 | return:string，如 'NULL' '计算所'
    Return: 
        标准化的字符串:string
    '''
    __version__ = 1.7
    __author__ = 'esue_yan@163.com' 
    
    
    def __init__(self,element,choice='strip'):
        self.element = element
        self.choice = choice

    def check_contain_chinese(self):
        '''
        检查字符串中英文状况，适配landinn数据库表现有数据
        规则：英文字母个数 > 总字符个数的一半
        :return: bool True-中文占比多 False-英文占比多
        '''
        temp = re.sub(r"\s|&nbsp;|&ensp;|&emsp;|&thinsp;","",self.element)
        len_all = len(temp)
        len_en = 0
        for i in temp:
            if i in string.ascii_letters:
                len_en += 1
        if 2*len_en <= len_all:
            return True
        else:
            return False
    
    def strQ2B(self):
        '''将字符串全角转换为半角'''
        rstring = ""
        for uchar in self.element:
            inside_code = ord(uchar)
            if inside_code == 0x3000:
                inside_code = 0x0020
            else:
                inside_code -= 0xfee0
            if not (0x0021 <= inside_code and inside_code <= 0x7e):
                rstring += uchar
                continue
            rstring += chr(inside_code)
        return rstring
    
    def removeAllSpace(self):
        '''去除字符串中的所有空格'''  
        self.element = re.sub(r"\s|&nbsp;|&ensp;|&emsp;|&thinsp;","",self.element)
        return self.element
    
    def strStrip(self):
        '''去除英文字符串的首尾空格''' 
        self.element = re.sub(r"&nbsp;|&ensp;|&emsp;|&thinsp;"," ",self.element)
        self.element = re.sub(r"(^\s*)|(\s*$)","",self.element)
        return self.element
    
    def standardization(self):
        '''字符串标准化'''
        self.element = self.strQ2B()
        if self.check_contain_chinese() and self.choice == 'allSpace':
            self.element = self.removeAllSpace()
            self.element = trd2smp(self.element)
        else:
            self.element = self.strStrip() 
            self.element = trd2smp(self.element)
        return self.element
    
    def mysql_format(self):
        '''
        数据类型转换+字符串标准化 用于mysql入landinn库时数据标准化
        :return: 'element'
        '''
        if self.element is None or self.element == "":
            return 'NULL'
        elif isinstance(self.element,str):
            self.element = self.standardization()
            self.element = escape_string(self.element)
        elif pd.isna(self.element):
            return 'NULL'  
        else:
            self.element = escape_string(str(self.element))
            return self.strQ2B()  
        return "'" + self.element + "'"