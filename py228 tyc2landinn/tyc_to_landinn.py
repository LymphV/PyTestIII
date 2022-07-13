#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import sqlalchemy
import pymysql
import time
import json
import re
import ast
import math
from sqlalchemy import create_engine
from pandas.io import sql
from datetime import datetime, timedelta, timezone
import traceback
import datetime
import requests
from urllib.parse import quote
import decimal
import os,sys
from tqdm import tqdm,trange
from colorama import Fore
import random
from decimal import Context,ROUND_HALF_UP
import random
from str_format import strFormat
from title_format import listToStr,titleFormat
from cp_pic import isValid,largePic

# 版本号 初始版-内测 #
__version__ = 'v1.2.19'

username = 'root'
password='linlei'
host = '10.208.63.46'

# 设定单次融合的企业数量 #
increment = 3000
# 天眼查数据标记 #
IS_BEIHANG = 20101
IS_BEIHANG_UPDATE = 20102
process = ['1. 查询或补全企业','2. 融合核心团队','3. 融合主要成员','4. 融合业务','5. 融合备案域名','6. 融合商标','7. 融合软著','8. 融合专利']
# path #
__path__  = os.path.dirname(os.path.abspath(__file__))

# 日志文件名称 #
def getToday():
    "获得今天的日期，格式为'%Y%m%d'"
    tz = timezone(timedelta(hours=8))
    return datetime.datetime.now(tz).strftime("%Y-%m-%d")

class ErrorLogName:
    def __init__ (this, file='error'):
        this.file = file
    def __fspath__ (this):
        return os.path.join(__path__, f'{this.file}{getToday()}.txt')
errorLogName = ErrorLogName()
# last_update_time:最后一条数据的update_at;this_updated_time:当前程序执行时间;execute_complete_time:程序执行完成的时间 #
expert_file = 'recordTYC.json'
expert_file = os.path.join(__path__, expert_file)
# 记录错误日志 #
errorlog = ErrorLogName('tyc_errLog')
# 记录执行日志 #
executelog = ErrorLogName('tyc_exeLog')
class log():          
    def exelog(*args):
        with open(executelog,'a',encoding='UTF-8') as error:
            print(*args, file=error)
            
    def errlog(*args):
        with open(errorlog,'a',encoding='UTF-8') as execute:
            print("错误位置：", *args, file=execute)

# 百度ak #
ak = "vEUPPLTEggaqbyGR41LwSxwOQcDQeL8C"
# 汇率 #
USD = decimal.Decimal("6.4965")
HKD = decimal.Decimal("0.8368")
TWD = decimal.Decimal("0.2311")
JPY = decimal.Decimal("0.05991")

def getNow():
    "获得此时的日期，格式为'%Y-%m-%d %H:%M:%S'"
    tz = timezone(timedelta(hours=8))
    return datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

def format_time(element):
    "毫秒时间戳转换datetime"
    if element is None or element == "" :
        return None
    elif math.isnan(float(element)):
        return None
    else :
        if int(element) < 0:
            element = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(element))
            element = (element + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            tz = timezone(timedelta(hours=8))
            dt = datetime.datetime.fromtimestamp(int(element)/1000, tz)
            element = str(dt.strftime('%Y-%m-%d %H:%M:%S'))
        return element

"生成ID"
i_seq = 0
last_time=0
def gen_ticket64(node):
    epoch = 1596816000000
    max_incr = pow(2,16)
    current_ms=int(time.time() * 1000)
    start_id = pow(10,18) 
    global i_seq , last_time 
    if last_time == 0 or current_ms-last_time >= 1000*5:
        last_time = current_ms
        i_seq = 0
    i_seq = i_seq+1
    incr = i_seq % max_incr
    return ((current_ms-epoch) << 22 | (node << 16) | (incr)) + start_id

"异常处理"
class UserMysqlException(Exception):
    "this is user's Exception for executed mysql insert or update sql but failed "
    def __init__(self,*args, **kwargs): 
        log.errlog(*args)
        self.args = args
        pass

    def __str__(self): 
        r= '自定义异常'
        for ar in self.args:
            r = r +',' + ar
        return r

"插入数据"
def insert_data(conn,table,value_clause):
    _sleep_time = random.randint(1,30)
    _retries_time = 0
    _max_retries_time = 600
    result = True
    while result and _retries_time <= _max_retries_time:
        try:
            insert_sql = "insert into {0} values {1};".format(table,value_clause)
            rtn = mycursor.execute(insert_sql)
            result = False
            return rtn
        except Exception as e:
            _retries_time += _sleep_time
            log.errlog("insert_data",str(e))
            print("等待",_sleep_time,"秒重新执行")
            time.sleep(_sleep_time)
            if _retries_time > _max_retries_time:
                raise UserMysqlException('insert_data出错',str(e))
        
"修改数据"
def update_data(conn,table, set_clause): 
    _sleep_time = random.randint(1,30)
    _retries_time = 0
    _max_retries_time = 600
    result = True
    while result :
        try:
            update_sql = "update {0} set {1}".format(table,set_clause)
            rtn = mycursor.execute(update_sql)
            result = False
            return rtn
        except Exception as e:
            _retries_time += _sleep_time
            log.errlog("update_data",str(e))
            print("等待",_sleep_time,"秒重新执行")
            time.sleep(_sleep_time)
            if _retries_time > _max_retries_time:
                raise UserMysqlException('update_data出错',str(e))

"查询数据"
def query_data(conn, table, where_clause):
    _sleep_time = random.randint(1,30)
    _retries_time = 0
    _max_retries_time = 600
    result = True
    while result :
        try:
            data = pd.read_sql('select * from {0} {1}'.format(table, where_clause), con=conn,coerce_float=False)
            result = False
            return data
        except Exception as e:
            _retries_time += _sleep_time
            log.errlog("query_data",str(e))
            print("等待",_sleep_time,"秒重新执行")
            time.sleep(_sleep_time)
            if _retries_time > _max_retries_time:
                raise UserMysqlException('query_data出错',str(e))


'''
融合机构--操作表 affiliations
    字段作废,'scope':'scope',并入business_scope
'''
def get_landinn_aff_id(einfo,origin):
    ename = str(einfo['name']).strip()
    einfo['is_beihang'] = IS_BEIHANG 
    affiliation_dict = {
        'affiliation_id':'aff_id',
        'tyc_id':'id',
        'is_beihang':'is_beihang',
        'alias':'alias',
        'display_name':'name',
        'display_name_en':'name_en',
        'reg_number':'regNumber',
        'credit_code':'creditCode',
        'tax_number':'taxNumber',       
        'legal_person_name':'legalPersonName',
        'reg_capital':'regCapital',
        'industry':'industry',
        'reg_location':'regLocation',
        'business_scope':'businessScope',
        'phone_number':'phoneNumber',
        'email':'email',
        'staff_num_range':'staffNumRange',
        'n_staff':'nStaff',
        'n_team_member':'nTeamMember',
        'n_product':'nProduct',
        'n_trademark':'nTrademark',
        'n_patent':'nPatent',
        'n_software_copyright':'nSoftwareCopyright',
        'n_website':'nWebsite',
        'establishment_time':'establishmentTime',
        'reg_province':'province',
        'reg_city':'city',
        'reg_capital_standard':'reg_capital_standard',
        'company_org_type':'companyOrgType',
        'is_new':'is_new',
        'category_score':'categoryScore',
        'percentile_score':'percentileScore',
        'email_list':'emailList',
        'phone_list':'phoneList',
        'weibo':'weibo',
        'base_info':'baseInfo',
        'entity_type':'entityType',
        'logo':'logo',
        'legal_person_id':'legalPersonId',
        'is_abroad':'isAbroad'
    } 
    if origin == 'tyc':
        einfo['is_new'] = 0

    try:
        if 'establishmentTime' in einfo.keys():
            einfo['establishmentTime'] = format_time(einfo['establishmentTime'])
            
        if 'scope' in einfo.keys() and 'businessScope' in einfo.keys():
            einfo['businessScope'] = einfo['scope'] if einfo['scope'] and not einfo['businessScope'] else einfo['businessScope']
            
        # 提取企业注册地址省市 并确定国内外企业 # 
        if 'regLocation' in einfo.keys():
            regLocation = einfo['regLocation']
            if regLocation and regLocation != "":
                reverse_geocoding = get_aff_province_city(regLocation[0:42])
                if reverse_geocoding and reverse_geocoding != "":
                    einfo['province'] = reverse_geocoding['province']
                    einfo['city'] = reverse_geocoding['city']
                    if reverse_geocoding['country'] and reverse_geocoding['country'] != "":
                        einfo['isAbroad'] = 0 if reverse_geocoding['country'] == '中国' else 1
                    
        # 标准化注册资金 # 
        if 'regCapital' in einfo.keys():
            einfo['reg_capital_standard'] = get_reg_capital_standard(einfo['regCapital'])

        # 判断landinn是否存在该企业 #  
        if 'id' in einfo and einfo['id'] and einfo['id'] != '': 
            landinn_aff = query_data(conn,'landinn.affiliations',"where is_deleted=0 and tyc_id = {} limit 1;".format(strFormat(einfo['id']).mysql_format()))
            if landinn_aff.empty:
                landinn_aff = query_data(conn,'landinn.affiliations',"where is_deleted=0 and display_name = {} limit 1;".format(strFormat(ename,'allSpace').mysql_format()))
        else:
            landinn_aff = query_data(conn,'landinn.affiliations',"where is_deleted=0 and display_name = {} limit 1;".format(strFormat(ename,'allSpace').mysql_format()))

        "不存在则在landinn新增"
        if landinn_aff.empty:
            aff_id = gen_ticket64(31) 
            einfo['aff_id'] = aff_id
            # 获取法人id #
            einfo['legalPersonId'] = get_legal_person_id(aff_id,einfo['legalPersonName'],einfo['legalPersonId']) if 'legalPersonName' in einfo and einfo['legalPersonName'] else None            
            if origin == 'new':  # 表示根据论文项目专利-机构关系新增数据，基本信息不完备 #
                einfo["is_new"] = 1
            table = "landinn.affiliations({0})"
            column_str = ','.join([key for key in affiliation_dict if key != 'display_name'])
            value_str = ','.join([strFormat(einfo.get(affiliation_dict[key])).mysql_format() for key in affiliation_dict if key != 'display_name'])
            #添加机构名称#
            column_str += ',display_name'  
            value_str += ','+strFormat(einfo.get(affiliation_dict['display_name']),'allSpace').mysql_format()                   
            table = table.format(column_str,value_str)
            rtn = insert_data(conn,table,"(" + value_str + ")")
            if rtn != 1:
                raise UserMysqlException('插入失败','insert_affiliations','影响行数不为1',str(rtn))
        else:
            "存在则 补充landinn机构信息"
            if landinn_aff['is_beihang'][0] == IS_BEIHANG:
                einfo['is_beihang'] = IS_BEIHANG
            else:
                einfo['is_beihang'] = IS_BEIHANG_UPDATE
            aff_id = landinn_aff['affiliation_id'][0]
            # 获取法人id #
            einfo['legalPersonId'] = get_legal_person_id(aff_id,einfo['legalPersonName'],einfo['legalPersonId']) if 'legalPersonName' in einfo and einfo['legalPersonName'] else None
            # 处理 entity_type #
            einfo['entityType'] = einfo['entityType'] if 'entityType' in einfo and not landinn_aff['entity_type'][0] else None
            set_clause = ''       
            for key in affiliation_dict:
                tyc_key = affiliation_dict.get(key)
                if key == 'display_name':
                    tyc_key_value = strFormat(einfo.get(tyc_key),'allSpace').mysql_format()
                else:
                    tyc_key_value = strFormat(einfo.get(tyc_key)).mysql_format() 
                if not tyc_key_value == 'NULL':
                    set_clause += '{} = {} ,'.format(key,tyc_key_value)
            set_clause += 'affiliation_id = {} where affiliation_id = {} '.format(strFormat(aff_id).mysql_format(),strFormat(aff_id).mysql_format())
            rtn = update_data(conn,'landinn.affiliations',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('get_landinn_aff_id出错',str(e))
    return aff_id
    
"获取法人id"
def get_legal_person_id(aff_id,name,tyc_person_id):
    
    if tyc_person_id:
        # 判断是否为人名 #
        is_human = query_data(conn,'tianyancha.human',"where id = {} limit 1;".format(strFormat(tyc_person_id).mysql_format()))
        if not is_human.empty:
            return get_landinn_author_id({'name':name,'aff_id':aff_id},aff_id,'new')
        else:
            # 判断是否为企业名 #
            is_aff = query_data(conn,'tianyancha.enterprise',"where id = {} limit 1;".format(strFormat(tyc_person_id).mysql_format()))
            if not is_aff.empty and name == is_aff['name'][0]:
                landinn_aff = query_data(conn,'landinn.affiliations',"where tyc_id = {} limit 1;".format(strFormat(tyc_person_id).mysql_format()))
                if landinn_aff.empty:
                    aff_id = gen_ticket64(31)
                    affiliation_dict = {'affiliation_id':aff_id,'tyc_id':tyc_person_id,'display_name':name,'is_beihang':IS_BEIHANG,'is_new':0}
                    table = "landinn.affiliations({0})"
                    column_str = ','.join([key for key in affiliation_dict if key != 'display_name'])
                    value_str = ','.join([strFormat(affiliation_dict[key]).mysql_format() for key in affiliation_dict if key != 'display_name'])
                    # 添加机构名称 #
                    column_str += ',display_name'  
                    value_str += ','+strFormat(affiliation_dict['display_name'],'allSpace').mysql_format()                   
                    table = table.format(column_str,value_str)
                    rtn = insert_data(conn,table,"(" + value_str + ")")
                    if rtn != 1:
                        raise UserMysqlException('插入失败','insert_affiliations','影响行数不为1',str(rtn))
                else:
                    aff_id = landinn_aff['affiliation_id'][0]
                return aff_id
            else:
                return None       
    else:
        return None
    
"注册资本转换"
def get_reg_capital_standard(regCapital):
    if regCapital is not None and regCapital != "" and regCapital != 'null':
        regCapitalStandard = exchange_rate(regCapital)
        return regCapitalStandard
    else:
        return ""
       
"汇率计算及标准化"
def exchange_rate(str1):
    sign1 = str1.find("万")
    sign2 = str1.find("美元")
    sign3 = str1.find("港元")
    sign4 = str1.find("新台币")
    sign5 = str1.find("日元")
    num_list = re.findall('(\d+)', str1)
    if len(num_list) == 1:
        num_str = ''.join(num_list)
        num = decimal.Decimal(num_str)
    else:
        num_str = '.'.join(num_list)
        num = decimal.Decimal(num_str)
    if sign1 > 0:
        num *= 10000
    if sign2 > 0:
        num *= USD
    elif sign3 > 0:
        num *= HKD
    elif sign4 > 0:
        num *= TWD
    elif sign5 > 0:
        num *= JPY
    final_num = int(num*100)
    if final_num == 0:
        return ""
    else:
        return final_num

"获取地理编码"
def http_get_geocoding(regLocation): 
    geoCoding = requests.get("http://api.map.baidu.com/geocoding/v3/?address=" + quote(regLocation, "utf-8") + "&output=json&ak=" + ak + "")
    geoCoding = eval(geoCoding.content.decode("utf-8"))
    if geoCoding['status'] == 0:
        return geoCoding['result']['location']
    elif geoCoding['status'] == 1:
        return geoCoding['results']
    else:
        raise  UserMysqlException('请求geoCoding接口出现错误：',geoCoding['message']) 
        
"逆地理编码"
def http_get_reverse_geocoding(longitude,latitude):
    reverse_geocoding = requests.get("http://api.map.baidu.com/reverse_geocoding/v3/?ak=" + ak + "&output=json&coordtype=wgs84ll&location=" + str(latitude) + "," + str(longitude) + "")
    reverse_geocoding = eval(reverse_geocoding.content.decode("utf-8"))
    if reverse_geocoding['status'] == 0:
        return reverse_geocoding['result']['addressComponent']
    elif reverse_geocoding['status'] == 1:
        return reverse_geocoding['results']
    else:
        raise  UserMysqlException('请求geoCoding接口出现错误：',reverse_geocoding['message']) 

"提取机构注册省和市"
def get_aff_province_city(regLocation):
    # 获取注册地址经纬度 #
    geoCoding = http_get_geocoding(regLocation)
    if geoCoding:
        longitude = geoCoding['lng']
        latitude = geoCoding['lat']
        # 根据经纬度获取省市 #
        reverse_geocoding = http_get_reverse_geocoding(longitude,latitude)
        if reverse_geocoding:
            return reverse_geocoding
        else:
            return ""
    else:
        return ""
        

'''
融合机构历史名称--操作表 affiliation_history_name 
'''
def insert_history_name(aff_id,einfo):
    try:
        aff_history_name = query_data(conn,'landinn.affiliation_history_name','where is_deleted = 0 and affiliation_id = "' + str(aff_id) + '";')
        historyNameList = einfo['historyNameList']
        "天眼查该字段非空时新增or补充"
        if historyNameList is not None:
            historyNameList = re.sub("|\'|\[|\]","", historyNameList)
            historyNameList = historyNameList.split(",") 
            "比较天眼查和landinn中的历史名称数量，不足则补全"
            if len(aff_history_name) < len(historyNameList):
                aff_history_name_list = aff_history_name.display_name
                value_str = ""
                for his_name in historyNameList:
                    if his_name not in aff_history_name_list.unique():
                        "补充历史机构名称"
                        value_str += ',({0},{1})'.format(aff_id,strFormat(his_name,'allSpace').mysql_format()) 
                insert_data(conn,'landinn.affiliation_history_name(affiliation_id,display_name)',re.sub(',', '', value_str, 1))
    except UserMysqlException as e:
        raise UserMysqlException('insert_history_name出错',str(e))


'''
融合作者--操作表 authors 并返回author_id
'''
def get_landinn_author_id(team,aff_id,origin):
    author_dict = {
        'tyc_id':'hid',
        'display_name':'name',
        'position':'position',
        'title':'title',
        'head_portrait':'icon',
        'brief':'description',
        'last_known_affiliation_id':'aff_id',
        'golaxy_author_id':'author_id' ,
        'is_beihang':'is_beihang',
        'is_new':'is_new'
    }
    team['is_beihang'] = IS_BEIHANG
    if origin == 'tyc':
        team['is_new'] = 0
    
    try:   
        "判断landinn是否存在该作者"
        landinn_author = query_data(conn,'landinn.authors',"where is_deleted !=1 and display_name = {0} and last_known_affiliation_id = {1} {2} ;"                                    .format(strFormat(team['name'],'allSpace').mysql_format(),strFormat(team['aff_id']).mysql_format(),'limit 1;'))
        "不存在则在landinn新增"
        if landinn_author.empty:
            author_id = gen_ticket64(31)
            team['author_id'] = author_id
            # 规格化title、position #
            if 'title' in team: team['title'] = titleFormat(team['title']) 
            if 'position' in team: team['position'] = titleFormat(team['position']) 
            if origin == 'new':
                team['is_new'] = 1
            table = "landinn.authors({0})"
            column_str = ','.join([key for key in author_dict if key != 'display_name'])
            value_str = ','.join([strFormat(team.get(author_dict[key])).mysql_format() for key in author_dict if key != 'display_name'])
            #添加作者姓名#
            column_str += ',display_name'  
            value_str += ','+strFormat(team.get(author_dict['display_name']),'allSpace').mysql_format()
            table = table.format(column_str)
            rtn = insert_data(conn,table,"(" + value_str + ")")
            if rtn != 1:
                raise UserMysqlException('插入失败','insert_authors','影响行数不为1',str(rtn))
        else:
            "存在则进行补充"
            author_id = landinn_author['golaxy_author_id'][0]
            if landinn_author['is_beihang'][0] == IS_BEIHANG:
                team['is_beihang'] = IS_BEIHANG
            else:
                team['is_beihang'] = IS_BEIHANG_UPDATE
            # 处理多源title、position融合 #
            if 'title' in team: team['title'] = titleFormat(landinn_author['title'][0],team['title']) 
            if 'position' in team: team['position'] = titleFormat(landinn_author['position'][0],team['position']) 
            # 处理头像 # 
            if 'icon' in team and team['icon']:
                head_portrait = landinn_author['head_portrait'][0] if isValid(landinn_author['head_portrait'][0]) else None
                icon = team['icon'] if isValid(team['icon']) else None
                team['icon'] = largePic({'p1':head_portrait,'p2':icon})
            
            set_clause = ''       
            for key in author_dict:
                tyc_key = author_dict.get(key)
                if key == 'display_name':
                    tyc_key_value = strFormat(team.get(tyc_key),'allSpace').mysql_format()          
                else:
                    tyc_key_value = strFormat(team.get(tyc_key)).mysql_format()
                if not tyc_key_value == 'NULL':
                    set_clause += '{} = {} ,'.format(key,tyc_key_value)
            set_clause += 'golaxy_author_id = {} where golaxy_author_id = {} '.format(strFormat(author_id).mysql_format(),strFormat(author_id).mysql_format())
            rtn = update_data(conn,'landinn.authors',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('get_landinn_author_id出错',str(e))      
    return author_id
                

'''
融合团队成员
'''
def merge_team_member(eid, aff_id):
    team_dict = {
        'affiliation_id':'aff_id',
        'author_id':'author_id',
        'author_name':'name',
        'title':'title',
        'is_dimision':'isDimision',
        'icon':'icon',
        'description':'description'
    }
    try:
        "根据eid查询团队"
        team_list = query_data(conn,'tianyancha.teamMember','where eid='+eid)
        for i,team in team_list.iterrows():
            team['aff_id'] = aff_id

            "插入或补全landinn中author信息，并返回author_id"
            author_id = get_landinn_author_id(team,aff_id,'tyc')
            team['author_id'] = author_id 

            landinn_team_member = query_data(conn,"landinn.affiliation_team_member","where is_deleted !=1 and author_id = " + str(author_id) + ";")
            "不存在则新增"
            if landinn_team_member.empty:
                insert_landinn_team_member(team,team_dict)
            else:
                "存在则修改补充"
                update_landinn_team_member(team,team_dict)
    except UserMysqlException as e:
        raise UserMysqlException('merge_team_member出错',str(e))

"修改团队成员"
def update_landinn_team_member(team,team_dict):
    try:
        set_clause = ''       
        for key in team_dict:
            tyc_key = team_dict.get(key)
            if key == 'author_name':
                tyc_key_value = strFormat(team.get(tyc_key),'allSpace').mysql_format()          
            else:
                tyc_key_value = strFormat(team.get(tyc_key)).mysql_format()                               
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'author_id = {0} where author_id = {1} and affiliation_id = {2}'.format(strFormat(team['author_id']).mysql_format(),strFormat(team['author_id']).mysql_format(),strFormat(team['aff_id']).mysql_format())
        rtn = update_data(conn,'landinn.affiliation_team_member',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_team_member出错',str(e))

"增加团队成员"
def insert_landinn_team_member(team,team_dict):
    try:
        table = "landinn.affiliation_team_member({0})"
        column_str = ','.join([key for key in team_dict if key != 'author_name'])
        value_str = ','.join([strFormat(team.get(team_dict[key])).mysql_format() for key in team_dict if key != 'author_name'])
        #添加作者姓名#
        column_str += ',author_name'  
        value_str += ','+strFormat(team.get(team_dict['author_name']),'allSpace').mysql_format()
        table = table.format(column_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_landinn_team_member','影响行数不为1',str(rtn))
    except UserMysqlException as e:
        raise UserMysqlException('insert_landinn_team_member出错',str(e))


'''
融合主要成员--操作表  affiliation_staff
'''
def merge_staff(eid, aff_id):
    staff_dict = {
        'affiliation_id':'aff_id',
        'staff_id':'staff_id',
        'staff_name':'name',
        'type':'type',
        'type_join':'typeJoin'
    }
    try: 
        # 根据eid查询核心成员 # 
        staff_list = query_data(conn,'tianyancha.staff','where eid=' + eid)
        for i,staff in staff_list.iterrows():
            staff['is_beihang'] = IS_BEIHANG
            staff['aff_id'] = aff_id
            if staff['type'] == 1 :
                # 机构 # 
                landinn_sid = get_landinn_aff_id({'id':staff['eid'],'name':staff['name'],'is_beihang':staff['is_beihang']},"new")
            else:
                # 作者 # 
                # 规格化tyc职位 #
                position = ast.literal_eval(staff['typeJoin']) if staff['typeJoin'] else ''
                position = ';'.join(strFormat(i).standardization() for i in position)
                landinn_sid = get_landinn_author_id({'aff_id':aff_id,'hid':staff['sid'],'name':staff['name'],'is_beihang':staff['is_beihang'],'position':position},aff_id,'new')           
            staff['staff_id'] = landinn_sid
            landinn_staff = query_data(conn,"landinn.affiliation_staff","where is_deleted = 0 and staff_id = " + str(landinn_sid) + ";")
            "不存在则新增"
            if landinn_staff.empty:
                insert_landinn_staff(staff,staff_dict)
            else:
                "存在则修改补充"
                update_landinn_staff(staff,staff_dict)
    except UserMysqlException as e:
        raise UserMysqlException('merge_staff出错',str(e))
            
"修改staff"
def update_landinn_staff(staff,staff_dict):
    try:
        set_clause = ''       
        for key in staff_dict:
            tyc_key = staff_dict.get(key)
            if key == 'staff_name':
                tyc_key_value = strFormat(staff.get(tyc_key),'allSpace').mysql_format()          
            else:
                tyc_key_value = tyc_key_value = strFormat(staff.get(tyc_key)).mysql_format()
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)

        set_clause += 'staff_id = {} where staff_id = {} '.format(strFormat(staff['staff_id']).mysql_format(),strFormat(staff['staff_id']).mysql_format())
        rtn = update_data(conn,'landinn.affiliation_staff',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_staff出错',str(e))
    
"新增staff"
def insert_landinn_staff(staff,staff_dict):
    try:
        table = "landinn.affiliation_staff({0})"
        column_str = ','.join([key for key in staff_dict if key != 'staff_name'])
        value_str = ','.join([strFormat(staff.get(staff_dict[key])).mysql_format() for key in staff_dict if key != 'staff_name'])
        #添加作者姓名#
        column_str += ',staff_name'  
        value_str += ','+strFormat(staff.get(staff_dict['staff_name']),'allSpace').mysql_format()
        table = table.format(column_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_landinn_staff','影响行数不为1',str(rtn))
    except UserMysqlException as e:
        raise UserMysqlException('insert_landinn_staff出错',str(e))
        

'''
融合业务--操作表  affiliation_product
'''
def merge_product(eid, aff_id):
    product_dict = {
        'golaxy_product_id':'product_id',
        'tyc_id':'eid',
        'affiliation_id':'aff_id',
        'hangye':'hangye',
        'yewu':'yewu',
        'product_name':'product',
        'logo':'logo',
        'setup_time':'setupTime',
        'is_beihang':'is_beihang'
    } 
    try:
        "根据eid查询业务"
        product_list = query_data(conn,'tianyancha.product','where eid = {}'.format(strFormat(eid).mysql_format()))

        for i,product in product_list.iterrows():
            product['is_beihang'] = IS_BEIHANG
            product['aff_id'] = aff_id
            product['setupTime'] = format_time(product['setupTime'])
            landinn_product = query_data(conn,"landinn.product","where is_deleted = 0 and tyc_id = {} and product_name = {};".format(strFormat(eid).mysql_format(),strFormat(product['product'],'allSpace').mysql_format()))
            if landinn_product.empty:
                "不存在则新增"
                product_id = gen_ticket64(31)
                product['product_id'] = product_id
                insert_landinn_product(product,product_dict)
            else:
                "存在则修改补充"
                if landinn_product['is_beihang'][0] == IS_BEIHANG:
                    product['is_beihang'] = IS_BEIHANG
                else:
                    product['is_beihang'] = IS_BEIHANG_UPDATE

                product['product_id'] = landinn_product['golaxy_product_id'][0]
                update_landinn_product(product,product_dict)
    except UserMysqlException as e:
        raise UserMysqlException('merge_product出错',str(e))

"修改业务"
def update_landinn_product(product,product_dict):
    try:
        set_clause = ''       
        for key in product_dict:
            tyc_key = product_dict.get(key)
            if key == 'product_name':
                tyc_key_value = strFormat(product.get(tyc_key),'allSpace').mysql_format() 
            else:
                tyc_key_value = strFormat(product.get(tyc_key)).mysql_format()
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)

        set_clause += 'golaxy_product_id = {} where golaxy_product_id = {} '.format(strFormat(product['product_id']).mysql_format(),strFormat(product['product_id']).mysql_format())
        rtn = update_data(conn,'landinn.product',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_product出错',str(e))
    
"新增业务"
def insert_landinn_product(product,product_dict):
    try:
        table = "landinn.product({0})"
        column_str = ','.join([key for key in product_dict if key != 'product_name'])
        value_str = ','.join([strFormat(product.get(product_dict[key])).mysql_format() for key in product_dict if key != 'product_name'])
        #添加产品名称#
        column_str += ',product_name'  
        value_str += ','+strFormat(product.get(product_dict['product_name']),'allSpace').mysql_format()
        table = table.format(column_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_landinn_product','影响行数不为1',str(rtn))   
    except UserMysqlException as e:
        raise UserMysqlException('insert_landinn_product出错',str(e))

'''
融合商标
'''
def merge_trademark(eid, aff_id):
    trademark_dict = {
        'golaxy_trademark_id':'trademark_id',
        'tyc_id':'id',
        'affiliation_id':'aff_id',
        'international_classification':'intCls',
        'trademark_title':'title',
        'registration_number':'regNo',
        'applicant_cn':'applicantCn',
        'trademark_picture':'pic',
        'is_beihang':'is_beihang'
    }
    try:
        "根据eid查询商标"
        trademark_list = query_data(conn,'tianyancha.trademark','where eid={}'.format(strFormat(eid).mysql_format()))

        for i,trademark in trademark_list.iterrows():
            trademark['aff_id'] = aff_id
            landinn_trademark = query_data(conn,"landinn.trademark","where is_deleted = 0 and tyc_id = {};".format(strFormat(trademark['id']).mysql_format()))
            if landinn_trademark.empty:
                "不存在则新增"
                trademark['is_beihang'] = IS_BEIHANG
                trademark_id = gen_ticket64(31)
                trademark['trademark_id'] = trademark_id            
                insert_landinn_trademark(trademark,trademark_dict)
            else:
                "存在则修改补充"
                if landinn_trademark['is_beihang'][0] == IS_BEIHANG:
                    trademark['is_beihang'] = IS_BEIHANG
                else:
                    trademark['is_beihang'] = IS_BEIHANG_UPDATE

                trademark['trademark_id'] = landinn_trademark['golaxy_trademark_id'][0]
                update_landinn_trademark(trademark,trademark_dict)
    except UserMysqlException as e:
        raise UserMysqlException('merge_trademark出错',str(e))

"修改商标"
def update_landinn_trademark(trademark,trademark_dict):
    try:
        set_clause = ''       
        for key in trademark_dict:
            tyc_key = trademark_dict.get(key)
            if key == 'trademark_title':
                tyc_key_value = strFormat(trademark.get(tyc_key),'allSpace').mysql_format()          
            else:
                tyc_key_value = strFormat(trademark.get(tyc_key)).mysql_format()
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)

        set_clause += 'golaxy_trademark_id = {} where golaxy_trademark_id = {} '.format(strFormat(trademark['trademark_id']).mysql_format(),strFormat(trademark['trademark_id']).mysql_format())
        rtn = update_data(conn,'landinn.trademark',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_trademark出错',str(e))

"新增商标"
def insert_landinn_trademark(trademark,trademark_dict):
    try:  
        table = "landinn.trademark({0})"
        column_str = ','.join([key for key in trademark_dict if key != 'trademark_title'])
        value_str = ','.join([strFormat(trademark.get(trademark_dict[key])).mysql_format() for key in trademark_dict if key != 'trademark_title'])
        #添加商标名称#
        column_str += ',trademark_title'  
        value_str += ','+strFormat(trademark.get(trademark_dict['trademark_title']),'allSpace').mysql_format()
        table = table.format(column_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_landinn_trademark','影响行数不为1',str(rtn)) 
    except UserMysqlException as e:
        raise UserMysqlException('insert_landinn_trademark出错',str(e))

'''
融合备案域名
'''
def merge_website(eid, aff_id):
    website_dict = {
        'affiliation_id':'aff_id',
        'website_id':'website_id',
        'web_name':'webName',
        'ym':'ym',
        'liscense':'liscense'
    }
    website_homepage_dict = {
        'homepage_url':'homepage_url',
        'website_id':'website_id'
    }
    try:
        "根据eid查询业务"
        website_list = query_data(conn,'tianyancha.website','where eid={}'.format(strFormat(eid).mysql_format()))   
        for i,website in website_list.iterrows():
            website['aff_id'] = aff_id       
            "website"
            landinn_website = query_data(conn,"landinn.affiliation_website","where is_deleted !=1 and ym = {};".format(strFormat(website['ym']).mysql_format()))
            if landinn_website.empty:
                "不存在则新增" 
                website['website_id'] = gen_ticket64(31)
                website_id = insert_landinn_website(website,website_dict)
            else:
                "存在则修改补充"
                website_id = landinn_website['website_id'][0]
                website['website_id'] = website_id
                update_landinn_website(website,website_dict)

            "website_homepage"        
            "天眼查该字段非空时新增or补充"
            if website['website'] is not None and not website['website'] == "":  
                weblist = ast.literal_eval(website['website'])   
                website_homepage = {}
                landinn_website_homepage = query_data(conn,'landinn.affiliation_website_homepage',"where is_deleted !=1 and website_id = {}".format(strFormat(website_id).mysql_format()))
                for homepage in weblist:
                    website_homepage['website_id'] = website_id
                    website_homepage['homepage_url'] = homepage
                    "比较天眼查和landinn中的homepage数量，不足则补全"
                    if len(landinn_website_homepage) < len(weblist):
                        insert_landinn_website_homepage(website_homepage,website_homepage_dict)
    except UserMysqlException as e:
        raise UserMysqlException('merge_website出错',str(e))
            
"修改website"
def update_landinn_website(website,website_dict):
    try:
        set_clause = ''       
        for key in website_dict:
            tyc_key = website_dict.get(key)
            tyc_key_value = strFormat(website.get(tyc_key)).mysql_format()
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'website_id = {} where website_id = {} '.format(strFormat(website['website_id']).mysql_format(),strFormat(website['website_id']).mysql_format())
        rtn = update_data(conn,'landinn.affiliation_website',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_website出错',str(e))
            
"新增website"
def insert_landinn_website(website,website_dict):
    try:
        table = "landinn.affiliation_website({0})"
        column_str = ','.join([key for key in website_dict])
        value_str = ','.join([strFormat(website.get(website_dict[key])).mysql_format() for key in website_dict])
        table = table.format(column_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_landinn_website','影响行数不为1',str(rtn))
        return website['website_id']
    except UserMysqlException as e:
        raise UserMysqlException('insert_landinn_website出错',str(e))

"新增website_homepage"
def insert_landinn_website_homepage(website_homepage,website_homepage_dict): 
    try:
        table = "landinn.affiliation_website_homepage({0})"
        column_str = ','.join([key for key in website_homepage_dict])
        value_str = ','.join([strFormat(website_homepage[website_homepage_dict[key]]).mysql_format() for key in website_homepage_dict])
        table = table.format(column_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_landinn_website_homepage','影响行数不为1',str(rtn))
    except UserMysqlException as e:
        raise UserMysqlException('insert_landinn_website_homepage出错',str(e))
        
        
'''
融合软著
'''
def merge_softright(eid, aff_id):
    softright_dict = {
        'golaxy_sc_id':'softright_id',
        'tyc_id':'id',
        'registration_number':'regNum',
        'version':'version',
        'full_name':'fullName',
        'registration_time':'regTime',    
        'event_time':'eventTime',
        'publish_time':'publishTime',
        'author_nationality':'authorNationality',
        'simple_name':'simpleName',
        'is_beihang':'is_beihang'
    }
    try:
        "根据eid查询软著"
        softright_list = query_data(conn,'tianyancha.softwareCopyright','where eid='+str(eid))   
        for i,softright in softright_list.iterrows():
            softright['aff_id'] = aff_id 
            softright['regTime'] = format_time(softright['regTime'])
            softright['eventTime'] = format_time(softright['eventTime'])
            softright['publishTime'] = format_time(softright['publishTime'])
            "新增softright,并返回softright_id"
            softright_id = get_landinn_softright(softright,softright_dict,aff_id)
    except UserMysqlException as e:
        raise UserMysqlException('merge_softright出错',str(e))

        
"新增softright,并返回softright_id"
def get_landinn_softright(softright,softright_dict,aff_id):  
    try:
        "查询landinn中是否存在该软著"
        softright_id = softright['id']
        landinn_softright = query_data(conn,'landinn.software_copyright','where is_deleted = 0 and tyc_id = {} limit 1;'.format(strFormat(softright_id).mysql_format())) 

        if landinn_softright.empty:
            "不存在则新增软著"
            softright['is_beihang'] = IS_BEIHANG
            softright_id = insert_landinn_softright(softright,softright_dict)
            "新增软著机构"
            softright['aff_id'] = aff_id
            insert_landinn_sc_aff(softright,softright_id)
        else:
            "存在则修改软著"
            if landinn_softright['is_beihang'][0] == IS_BEIHANG:
                softright['is_beihang'] = IS_BEIHANG
            else:
                softright['is_beihang'] = IS_BEIHANG_UPDATE

            softright_id = landinn_softright['golaxy_sc_id'][0]
            softright['softright_id'] = softright_id
            update_landinn_softright(softright,softright_dict)
    except UserMysqlException as e:
        raise UserMysqlException('get_landinn_softright出错',str(e))
    return softright_id


"新增softrigh_affiliation"
def insert_landinn_sc_aff(softright,softright_id):
    softright['softright_id'] = softright_id
    softright_affiliation_dict = {
        'sc_id':'softright_id',
        'tyc_id':'id',
        'affiliation_id':'aff_id',
        'tyc_aff_id':'eid'
    }  
    try:
        table = "landinn.softwareCopyright_affiliation({0})"
        column_str = ','.join([key for key in softright_affiliation_dict])
        value_str = ','.join([strFormat(softright.get(softright_affiliation_dict[key])).mysql_format() for key in softright_affiliation_dict])
        table = table.format(column_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','softwareCopyright_affiliation','影响行数不为1',str(rtn))
    except UserMysqlException as e:
        raise UserMysqlException('insert_landinn_sc_aff出错',str(e))

"修改软著"
def update_landinn_softright(softright,softright_dict):
    try:
        set_clause = ''       
        for key in softright_dict:
            tyc_key = softright_dict.get(key)
            if key == 'full_name':
                tyc_key_value = strFormat(softright.get(tyc_key),'allSpace').mysql_format()          
            else:
                tyc_key_value = strFormat(softright.get(tyc_key)).mysql_format()
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'golaxy_sc_id = {} where golaxy_sc_id = {} '.format(strFormat(softright['softright_id']).mysql_format(),strFormat(softright['softright_id']).mysql_format())
        rtn = update_data(conn,'landinn.software_copyright',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_softright出错',str(e))
        
"新增软著"
def insert_landinn_softright(softright,softright_dict):
    try:
        softright_id = gen_ticket64(31)
        softright['softright_id'] = softright_id
        table = "landinn.software_copyright({0})"
        column_str = ','.join([key for key in softright_dict if key != 'full_name'])
        value_str = ','.join([strFormat(softright.get(softright_dict[key])).mysql_format() for key in softright_dict if key != 'full_name'])
        #添加软著名称#
        column_str += ',full_name'  
        value_str += ','+strFormat(softright.get(softright_dict['full_name']),'allSpace').mysql_format()
        table = table.format(column_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_landinn_softright','影响行数不为1',str(rtn))
    except UserMysqlException as e:
        raise UserMysqlException('insert_landinn_softright出错',str(e))
    return softright_id

'''
融合专利
'''
def merge_patent(eid,aff_id):
    try:
        # 根据eid查询专利 #
        patent_list = query_data(conn,'tianyancha.patent','where eid = {}'.format(strFormat(eid).mysql_format())) 
        num = 0
        for i,patent in patent_list.iterrows(): 
            num += 1
            patent_inventor = patent['inventor']  # tyc发明人 #
            patent_applicationNameList = patent['applicationNameList'] # tyc申请人 #
            # 插入或补全landinn中patent信息，并返回patent_id #
            patent_id = get_landinn_patent_id(patent)
            
            #  融合专利申请人 #
            patent_applicants_list = query_data(conn,'landinn.patent_applicants','where is_deleted = 0 and patent_id = '+ str(patent_id))                 
            # 规格化tyc专利申请人 #
            if patent_applicationNameList and not patent_applicationNameList.isspace():
                if(patent_applicationNameList.find('[')) != -1:
                    list = ast.literal_eval(patent_applicationNameList)
                    app_name_list = ';'.join(i for i in list)
                    patent_application = app_name_list.split(';')
                else:
                    patent_application = patent_applicationNameList.split(',')
                patent_application = [strFormat(i,'allSpace').standardization() for j,i in zip(range(0,len(patent_application)),patent_application) if i not in patent_application[:j]]
                merge_patent_application(patent_applicants_list,patent_application,patent_id,aff_id) 
                
            #  融合专利发明人 #
            select = 'patent_id,cast(author_id as char) as author_id,author_sequence_number,original_author,is_beihang,id '
            where_clause = 'where is_deleted = 0 and patent_id = {} order by author_sequence_number asc'.format(patent_id)
            patent_authors_list = pd.read_sql('select {0} from landinn.patent_authors {1}'.format(select,where_clause), con=conn,coerce_float=False)
            if patent_inventor and not patent_inventor.isspace():
                # 规格化tyc专利发明人 #
                patent_inventor = patent_inventor.split(';')
                patent_inventor_list = [strFormat(i,'allSpace').standardization() for j,i in zip(range(0,len(patent_inventor)),patent_inventor) if i not in patent_inventor[:j]]
                merge_patent_author(patent_authors_list,patent_inventor_list,patent_application,aff_id,patent_id)           
        log.exelog(num)
    except UserMysqlException as e:
        log.exelog(num)
        raise UserMysqlException('merge_patent出错',str(e))
  
'''
融合专利申请人
'''
def merge_patent_application(patent_applicants_list,patent_application,patent_id,aff_id):
    try:
        papplicant_dict = {
            'patent_id':'patent_id',
            'applicant_id':'applicant_id',
            'applicant_sequence_number':'seq',
            'original_applicant':'name',
            'applicant_type':'applicant_type',
            'is_beihang':'is_beihang' 
        }    
        # 规格化 landinn申请人 #
        applicant_list = patent_applicants_list.original_applicant 
        applicant_list = list(set(strFormat(app,'allSpace').standardization() for app in applicant_list))
        seq = 0
        for applicant in patent_application:
            seq += 1
            applicant = strFormat(applicant,'allSpace').standardization()
            # 企业名 #
            if len(applicant) >= 4:
                # 补充机构 -- 专利申请人 #
                app_aff_id = get_landinn_aff_id({'name':applicant},"new")
                if applicant not in applicant_list:  
                    papplicant = {'patent_id':patent_id,'applicant_id':app_aff_id,'applicant_type':1,'seq':seq,'name':applicant,'is_beihang':IS_BEIHANG}
                    insert_patent_applicants(papplicant,papplicant_dict)
                else:
                    papplicant = {'patent_id':patent_id,'applicant_id':app_aff_id,'applicant_type':1,'seq':seq,'name':applicant,'is_beihang':IS_BEIHANG_UPDATE}
                    update_patent_applicants(papplicant,papplicant_dict)
            # 人名 #
            else: 
                where_clause = "where is_deleted = 0 and patent_id = {0} and original_author = '{1}'".format(patent_id,applicant)
                patent_person = pd.read_sql('select cast(author_id as char) as author_id from landinn.patent_authors {}'.format(where_clause), con=conn, coerce_float=False)
                if patent_person.empty:
                    author_id = ''
                else:
                    if patent_person['author_id'][0] and not patent_person['author_id'][0].isspace():
                        author_id = patent_person['author_id'][0]
                    else:
                        author_id = ''
                papplicant = {'patent_id':patent_id,'applicant_id':author_id,'applicant_type':2,'seq':seq,'name':applicant,'is_beihang':IS_BEIHANG}
                if applicant not in applicant_list:
                    insert_patent_applicants(papplicant,papplicant_dict)  
                else:
                    update_patent_applicants(papplicant,papplicant_dict)  
    except UserMysqlException as e:
        raise UserMysqlException('merge_patent_application出错',str(e))
        
'''
融合专利发明人
'''
def merge_patent_author(patent_authors_list,patent_inventor_list,patent_applicationNameList,aff_id,patent_id):
    patent_author_dict = {
        'patent_id':'patent_id',
        'author_id':'author_id',
        'author_sequence_number':'seq',
        'original_author':'name',
        'is_beihang':'is_beihang',
        'id':'add_id'
    }
    inventor_list = patent_authors_list.original_author # landinn发明人 #

    seq = 0
    try:
        for inventor in patent_inventor_list: 
            seq += 1
            inventor = strFormat(inventor,'allSpace').standardization()
            if inventor.find('其他') >= 0:
                continue
            if inventor.find('不公告设计人') >= 0:
                continue  
            if not patent_authors_list.empty and inventor in inventor_list.unique():
                landinn_inventor = patent_authors_list[patent_authors_list['original_author'].isin([inventor])]
                index = landinn_inventor.index.values[0]
                landinn_authorId = landinn_inventor.loc[index,'author_id']
                landinn_isbeihang = landinn_inventor.loc[index,'is_beihang']
                add_id = landinn_inventor.loc[index,'id']
  
            # =1 可确认发明人机构 insert authors + patent_authors #
            if len(patent_applicationNameList) == 1:
                if inventor not in inventor_list.unique():
                    # + authors is_new=1 专利发明人 #
                    author_id = get_landinn_author_id({'aff_id':aff_id,'name':inventor}, aff_id,'new')
                    pauthor = {'patent_id':patent_id,'author_id':author_id,'seq':seq,'name':inventor,'is_beihang':IS_BEIHANG}
                    insert_patent_author(pauthor,patent_author_dict)
                else:
                    # 关系表author_id不为空时 #
                    if landinn_authorId and not landinn_authorId.isspace():
                        is_landinn_author = query_data(conn,'landinn.authors','where is_deleted = 0 and golaxy_author_id = {}'.format(landinn_authorId))
                        # 作者表不存在则需要新增 #
                        if is_landinn_author.empty:
                            author_id = get_landinn_author_id({'aff_id':aff_id,'name':inventor}, aff_id,'new')
                            pauthor = {'patent_id':patent_id,'author_id':author_id,'seq':seq,'name':inventor,'is_beihang':IS_BEIHANG,'add_id':add_id}
                            update_patent_author(pauthor,patent_author_dict)
                        else:
                            pauthor = {'patent_id':patent_id,'author_id':landinn_authorId,'seq':seq,'name':inventor,'is_beihang':IS_BEIHANG_UPDATE,'add_id':add_id}
                            update_patent_author(pauthor,patent_author_dict)
                    # 关系表author_id为空时 #
                    else:
                        # + authors is_new=1 专利发明人 #
                        author_id = get_landinn_author_id({'aff_id':aff_id,'name':inventor}, aff_id,'new')
                        pauthor = {'patent_id':patent_id,'author_id':author_id,'seq':seq,'name':inventor,'is_beihang':IS_BEIHANG,'add_id':add_id}
                        update_patent_author(pauthor,patent_author_dict)  
            # 不可确认发明人机构 udpate authors + patent_authors #
            else:
                # 判断该发明人是否存在于landinn中 存在进一步处理 #
                if inventor in inventor_list.unique():
                    # 关系表author_id不为空时 #
                    if landinn_authorId and not landinn_authorId.isspace():
                        is_landinn_author = query_data(conn,'landinn.authors','where is_deleted = 0 and golaxy_author_id = {}'.format(landinn_authorId))
                        if is_landinn_author.empty:
                            # 修改论文关系表的 author_id=null
                            author_id = ""
                            pauthor = {'patent_id':patent_id,'author_id':author_id,'seq':seq,'name':inventor,'is_beihang':IS_BEIHANG_UPDATE,'add_id':add_id}
                            update_patent_author(pauthor,patent_author_dict)  
                        else:
                            # 若author表存在该学者 则 修改该作者的 author表 upadted_at #
                            update_20101_author({'author_id':landinn_authorId,'updated_at':str(getNow())})
                            # 修改论文关系表的 author_id=null #
                            author_id = ""
                            pauthor = {'patent_id':patent_id,'author_id':author_id,'seq':seq,'name':inventor,'is_beihang':IS_BEIHANG_UPDATE,'add_id':add_id}
                            update_patent_author(pauthor,patent_author_dict) 
                    else:
                        pauthor = {'patent_id':patent_id,'author_id':landinn_authorId,'seq':seq,'name':inventor,'is_beihang':IS_BEIHANG_UPDATE,'add_id':add_id}
                        update_patent_author(pauthor,patent_author_dict)
                else:
                    # 补充专利发明人 + patent_authors author_id=null #
                    author_id = ""
                    pauthor = {'patent_id':patent_id,'author_id':author_id,'seq':seq,'name':inventor,'is_beihang':IS_BEIHANG}
                    insert_patent_author(pauthor,patent_author_dict)  
    except UserMysqlException as e:
        raise UserMysqlException('merge_patent_author出错',str(e))

def insert_patent_applicants(papplicant,papplicant_dict):
    "新增专利申请人"
    try:
        table = "landinn.patent_applicants({0})"
        column_str = ','.join([key for key in papplicant_dict if key != 'original_applicant'])
        value_str = ','.join([strFormat(papplicant.get(papplicant_dict[key]),'allSpace').mysql_format() for key in papplicant_dict if key != 'original_applicant'])
        #添加发明人姓名#
        column_str += ',original_applicant'  
        value_str += ','+strFormat(papplicant.get(papplicant_dict['original_applicant']),'allSpace').mysql_format()
        table = table.format(column_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_patent_applicants','影响行数不为1',str(rtn))
    except UserMysqlException as e:
        raise UserMysqlException('insert_patent_applicants出错',str(e))
        
def update_patent_applicants(papplicant,papplicant_dict):
    "修改专利申请人"
    try:
        set_clause = '' 
        for key in papplicant_dict:
            tyc_key = papplicant_dict.get(key)
            if key == 'original_author':
                tyc_key_value = strFormat(papplicant.get(tyc_key),'allSpace').mysql_format()          
            else:
                tyc_key_value = strFormat(papplicant.get(tyc_key)).mysql_format()
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'patent_id = {} where patent_id = {} and applicant_id = {};'.format(strFormat(papplicant['patent_id']).mysql_format(),strFormat(papplicant['patent_id']).mysql_format(),strFormat(papplicant['applicant_id']).mysql_format())
        rtn = update_data(conn,'landinn.patent_applicants',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_patent_applicants',str(e))  
             
def update_20101_author(author):
    "修改tyc新增的专家"
    tyc_author_dict = {
        'golaxy_author_id':'author_id',
        'updated_at':'updated_at'
    }  
    try:
        set_clause = '' 
        for key in tyc_author_dict:
            tyc_key = tyc_author_dict.get(key)
            tyc_key_value = strFormat(author.get(tyc_key)).mysql_format()
            set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'golaxy_author_id = {} where golaxy_author_id = {} '.format(strFormat(author['author_id']).mysql_format(),strFormat(author['author_id']).mysql_format())
        rtn = update_data(conn,'landinn.`authors`',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_20101_author出错',str(e))  

def update_patent_author(pauthor,patent_author_dict):
    "修改专利发明人"
    try:
        set_clause = '' 
        for key in patent_author_dict:
            tyc_key = patent_author_dict.get(key)
            if key == 'original_author':
                tyc_key_value = strFormat(pauthor.get(tyc_key),'allSpace').mysql_format()          
            else:
                tyc_key_value = strFormat(pauthor.get(tyc_key)).mysql_format()
            if not tyc_key_value == 'NULL' or tyc_key == 'author_id':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'patent_id = {} where id = {} '.format(strFormat(pauthor['patent_id']).mysql_format(),strFormat(pauthor['add_id']).mysql_format())
        rtn = update_data(conn,'landinn.patent_authors',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_patent_author出错',str(e))   
                                                                                          
def insert_patent_author(pauthor,patent_author_dict):
    "新增专利发明人"
    pauthor['is_beihang'] = IS_BEIHANG
    try:
        table = "landinn.patent_authors({0})"
        column_str = ','.join([key for key in patent_author_dict if key != 'original_author'])
        value_str = ','.join([strFormat(pauthor.get(patent_author_dict[key])).mysql_format() for key in patent_author_dict if key != 'original_author'])
        #添加作者姓名#
        column_str += ',original_author'  
        value_str += ','+strFormat(pauthor.get(patent_author_dict['original_author']),'allSpace').mysql_format()
        table = table.format(column_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_patent_author','影响行数不为1',str(rtn))   
    except UserMysqlException as e:
        raise UserMysqlException('insert_patent_author出错',str(e))
            

'''
融合专利 -- 操作表patent 并返回patent_id
'''
def get_landinn_patent_id(patent):
    patent['is_beihang'] = IS_BEIHANG
    patent_dict = {
        'golaxy_patent_id':'patent_id',
        'tyc_id':'id',
        'uuid':'uuid',
        'patent_title':'title',
        'applicant_number':'appNumber',
        'publication_number':'pubNumber',
        'patent_no':'patentNumber',
        'all_cat_number':'allCatNumber',
        'legal_status':'lawStatus',
        'applicant_date':'applicationTime',
        'publication_date':'pubDate',
        'application_publish_date':'applicationPublishTime',
        'inventor':'inventor',
        'agency_person_name':'agent',
        'agency_org_name':'agency',
        'applicant_address':'address',
        'patent_type':'patentType',
        'is_beihang':'is_beihang'
    }
    try:
        "判断landinn是否存在该专利"
        # publication_number不为空#
        landinn_patent = is_patent_exist(patent)
        
        "不存在则在landinn新增"
        if landinn_patent.empty: 
            "新增专利"
            patent_id = insert_landinn_patent(patent,patent_dict)
            "新增专利摘要"
            if patent['abstract'] is not None and not patent['abstract'] == "":
                "判断landinn是否存在该专利摘要"
                landinn_patent_abstracts = query_data(conn,"landinn.patent_abstracts","where is_deleted = 0 and patent_id = {};".format(strFormat(patent_id).mysql_format()))
                if landinn_patent_abstracts.empty:
                    insert_landinn_patent_abstracts(patent)
        else:
            if landinn_patent['is_beihang'][0] == IS_BEIHANG:
                patent['is_beihang'] = IS_BEIHANG
            else:
                patent['is_beihang'] = IS_BEIHANG_UPDATE
            patent_id = landinn_patent['golaxy_patent_id'][0]
            patent['patent_id'] = patent_id
            update_landinn_patent(patent,patent_dict)
            "新增专利摘要"
            if patent['abstract'] is not None and not patent['abstract'] == "":
                "判断landinn是否存在该专利摘要"
                landinn_patent_abstracts = query_data(conn,"landinn.patent_abstracts","where is_deleted = 0 and patent_id = {};".format(strFormat(patent_id).mysql_format()))
                if landinn_patent_abstracts.empty:
                    insert_landinn_patent_abstracts(patent)
                else:
                    update_landinn_patent_abstracts(patent)
    except UserMysqlException as e:
        raise UserMysqlException('get_landinn_patent_id出错',str(e))
    return patent_id

def is_patent_exist(patent):
    "判断专利是否已存在"

    # 公布号 #
    if patent['pubNumber'] and not patent['pubNumber'].isspace():
        landinn_patent = query_data(conn,"landinn.patent","where is_deleted = 0 and publication_number = {} limit 1;".format(strFormat(patent['pubNumber']).mysql_format()))
        if not landinn_patent.empty:
            return landinn_patent

    # 专利号 #
    if patent['patentNumber'] and not patent['patentNumber'].isspace():
        landinn_patent = query_data(conn,"landinn.patent","where is_deleted = 0 and patent_no = {} limit 1;".format(strFormat(patent['patentNumber']).mysql_format()))
        if not landinn_patent.empty:
            return landinn_patent
        
    # 专利标题#
    if patent['title'] and not patent['title'].isspace():
        landinn_patent = query_data(conn,"landinn.patent","where is_deleted = 0 and patent_title = {} limit 1;".format(strFormat(patent['title']).mysql_format()))
        if not landinn_patent.empty:
            return landinn_patent
        
    return pd.DataFrame()
        

def update_landinn_patent(patent,patent_dict):
    "修改论文"
    try:
        set_clause = '' 
        for key in patent_dict:
            tyc_key = patent_dict.get(key)
            if key == 'patent_title':
                tyc_key_value = strFormat(patent.get(tyc_key),'allSpace').mysql_format()          
            else:
                tyc_key_value = strFormat(patent.get(tyc_key)).mysql_format()
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'golaxy_patent_id = {} where golaxy_patent_id = {} '.format(strFormat(patent['patent_id']).mysql_format(),strFormat(patent['patent_id']).mysql_format())
        rtn = update_data(conn,'landinn.patent',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_patent出错',str(e))
                     
def insert_landinn_patent_abstracts(patent):  
    "新增专利摘要"
    try:
        rtn = insert_data(conn,"landinn.patent_abstracts(patent_id,patent_abstract)","({0},{1})".format(strFormat(patent['patent_id']).mysql_format(),strFormat(patent['abstract']).mysql_format()))
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_landinn_patent_abstracts','影响行数不为1',str(rtn))
    except UserMysqlException as e:
        raise UserMysqlException('insert_landinn_patent_abstracts出错',str(e))

def update_landinn_patent_abstracts(patent):  
    "修改专利摘要"
    try:
        set_clause = ""    
        set_clause += 'patent_id = {},patent_abstract = {} where patent_id = {} '.format(strFormat(patent['patent_id']).mysql_format(),strFormat(patent['abstract']).mysql_format(),strFormat(patent['patent_id']).mysql_format())
        rtn = update_data(conn,'landinn.patent_abstracts',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_patent_abstracts出错',str(e))
               
def insert_landinn_patent(patent,patent_dict): 
    "新增论文"
    patent_id = gen_ticket64(31) 
    patent['patent_id'] = patent_id    
    try:
        table = "landinn.patent({0})"
        column_str = ','.join([key for key in patent_dict if key != 'patent_title'])
        value_str = ','.join([strFormat(patent.get(patent_dict[key])).mysql_format() for key in patent_dict if key != 'patent_title'])
        #添加作者姓名#
        column_str += ',patent_title'  
        value_str += ','+strFormat(patent.get(patent_dict['patent_title']),'allSpace').mysql_format()
        table = table.format(column_str,value_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_landinn_patent','影响行数不为1',str(rtn)) 
    except UserMysqlException as e:
        raise UserMysqlException('insert_landinn_patent出错',str(e))
    return patent_id


"计算执行批次"
def get_execute_times(lu_time,tu_time):
    try:
        num_data = pd.read_sql("select count(*) as count from tianyancha.enterprise where updated_at between '" + str(lu_time) + "' and '" + str(tu_time) + "';", con=conn)
        num = int(num_data['count'][0])
        execute_times = math.ceil(num/increment)
    except UserMysqlException as e:
        raise UserMysqlException('get_execute_times出错',str(e))
    return execute_times
 

def start_execute():
    global conn
    global mycursor
    conn = pymysql.connect(host = host,port=3306,user = username,passwd = password,charset="utf8")
    mycursor = conn.cursor()

    this_updated_at = datetime.datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    record_df = pd.read_json(expert_file,lines=True,orient='records')  
    lu_time = record_df['last_updated_time'][0]
    tu_time = this_updated_at
    execute_times = get_execute_times(lu_time,tu_time)
    start_num = 0
    temp_num = 0
    
    print('*************************','\n')
    print('本次需融合',execute_times,'批数据','\n')
    print('*************************')
    log.exelog('*************************')
    log.exelog('本次需融合',execute_times,'批数据')
    log.exelog('*************************')
    try:
        for index in range(execute_times):
            conn = pymysql.connect(host = host,port=3306,user = username,passwd = password,charset="utf8")
            mycursor = conn.cursor()
            start_num = temp_num
            temp_num += increment
            print('融合第',index+1,'批企业')
            log.exelog('融合第',index+1,'批企业')
            record_df = tyc_to_landinn(lu_time,tu_time,record_df,start_num)
            time.sleep(random.randint(10,30))

        record_df['last_updated_time'] = [tu_time]
        record_df['execute_complete_time'] = [datetime.datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")]     
        record_df.to_json(expert_file,orient='records',lines=True)
    except UserMysqlException as e:
        raise UserMysqlException('执行有异常','start_execute')     
    return 1
    
    
def tyc_to_landinn(lu_time,tu_time,record_df,start_num):
    # 查询天眼查企业数据 -- enterprise #
    e_list = query_data(conn,"tianyancha.enterprise","where updated_at between '" + str(lu_time) + "' and '" + str(tu_time) + "' limit " + str(start_num) + "," + str(increment) + ";")

    eid_list = e_list['id']
    ename_list = e_list['name']
    
    print('查询到待融合企业数量：', len(e_list))
    log.exelog('查询到待融合企业数量：', len(e_list))   
    time.sleep(1)
    try :
        # 遍历企业    
        for i,einfo in e_list.iterrows():  
            with tqdm(process, leave=True, ncols=110, bar_format='{l_bar}%s{bar}%s{r_bar}' % (Fore.GREEN, Fore.RESET)) as t:           
                "若天眼查企业名为空则跳过"
                if einfo['name'] is  None or einfo['name'] == "":
                    log.exelog('企业',einfo['id'],'该企业数据为空')
                    t.set_description("融合第%i个企业--%s %s "%(i+1,einfo['id'],"该企业数据为空"))
                else:
                    log.exelog('融合第',i+1,'个企业：', einfo['name'])
                    eid = str(einfo['id'])
                    record_df['eid'] = [eid]
                    if not isinstance(record_df['last_updated_time'][0], str):
                        record_df['last_updated_time'] = [record_df['last_updated_time'][0].strftime("%Y-%m-%d %H:%M:%S")]
                    if not isinstance(record_df['execute_complete_time'][0], str):
                        record_df['execute_complete_time'] = [record_df['execute_complete_time'][0].strftime("%Y-%m-%d %H:%M:%S")]
                    record_df.to_json(expert_file,orient='records',lines=True)

                    for description in t:
                        t.set_description("融合第%i个企业--%s %s "%(i+1,einfo['name'],description))
                        if description == '1. 查询或补全企业':
                            log.exelog('\t','1. 查询或补全企业')
                            aff_id = get_landinn_aff_id(einfo,"tyc")
                            log.exelog('\t\t','1.1. 融合机构历史名称')
                            insert_history_name(aff_id,einfo)
                        if description == '2. 融合核心团队':
                            log.exelog('\t','2. 融合核心团队')
                            merge_team_member(eid, aff_id)
                        if description == '3. 融合主要成员':
                            log.exelog('\t','3. 融合主要成员')
                            merge_staff(eid, aff_id)
                        if description == '4. 融合业务':
                            log.exelog('\t','4. 融合业务')
                            merge_product(eid, aff_id)
                        if description == '5. 融合备案域名':
                            log.exelog('\t','5. 融合备案域名')
                            merge_website(eid, aff_id)
                        if description == '6. 融合商标':
                            log.exelog('\t','6. 融合商标')
                            merge_trademark(eid, aff_id)
                        if description == '7. 融合软著':
                            log.exelog('\t','7. 融合软著')
                            merge_softright(eid, aff_id)
                        if description == '8. 融合专利':
                            log.exelog('\t','8. 融合专利')
                            merge_patent(eid,aff_id)
                conn.commit()       
        print('*************************','\n')
        print('所有企业融合完成','\n')
        print('*************************','\n')
        log.exelog('*************************')
        log.exelog('所有企业融合完成')
        log.exelog('*************************')
        return record_df 
    except UserMysqlException as e:       
        log.errlog(str(e))
        conn.rollback()
        raise UserMysqlException('执行异常','tyc_to_landinn','程序执行错误')      
    finally:      
        mycursor.close()
        conn.close()

            
if __name__ == '__main__':
    start_execute()
            





