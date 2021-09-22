#!/usr/bin/env python
# coding: utf-8

# In[43]:


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

# 版本号 初始版-内测 #
__version__ = 'v1.1.9-a'

username = 'root'
password='linlei'
host = '10.208.63.47'

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
    def __fspath__ (this):
        return os.path.join(__path__, f'error{getToday()}.txt')

errorLogName = ErrorLogName()

# last_update_time:最后一条数据的update_at;this_updated_time:当前程序执行时间;execute_complete_time:程序执行完成的时间 #
expert_file = 'recordTYC.json'
expert_file = os.path.join(__path__, expert_file)
# 记录错误日志 #
errorlog = os.path.join(__path__, f'tyc_errLog{getToday()}.txt')
# 记录执行日志 #
executelog = os.path.join(__path__, f'tyc_exeLog{getToday()}.txt')
class log():
    def __errlog__(str):
        with open(errorlog,'a',encoding='UTF-8') as error:
            error.write(str)
            
    def __exelog__(*args):
        rr = args 
        r = ""
        for ar in rr:
            r = r +''+ str(ar)
        with open(executelog,'a',encoding='UTF-8') as execute:
            execute.write(r)
            
    def __exeerrlog__(*args):
        rr = args 
        r = "错误位置"
        for ar in rr:
            r = r +',' + str(ar)
        with open(errorlog,'a',encoding='UTF-8') as execute:
            execute.write(r+'\n')

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

"毫秒时间戳转换datetime"
def format_time(element):
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
    
"数据类型转换"
def format_conversion(element):
    if element is None or element == "" :
        return 'NULL'
    elif isinstance(element,str) :
        element = element.replace("'","''")
        element = "'" + element + "'"        
    elif  math.isnan(element)  :
        return 'NULL'  
    else :
        return str(element)    
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
        self.args = args
        pass

    def __str__(self): 
        r= '自定义异常'
        for ar in self.args:
            r = r +',' + ar
            log.__errlog__(r)
        return r

"插入数据"
def insert_data(conn,table,value_clause):
    
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
            log.__exeerrlog__("insert_data",str(e))
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
            log.__exeerrlog__("update_data",str(e))
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
            data = pd.read_sql('select * from {0} {1}'.format(table, where_clause), con=conn)
            result = False
            return data
        except Exception as e:
            _retries_time += _sleep_time
            log.__exeerrlog__("query_data",str(e))
            print("等待",_sleep_time,"秒重新执行")
            time.sleep(_sleep_time)
            if _retries_time > _max_retries_time:
                raise UserMysqlException('query_data出错',str(e))


'''
融合机构--操作表 affiliations
'''
def get_landinn_aff_id(einfo):
    ename = str(einfo['name'])
    einfo['is_beihang'] = IS_BEIHANG 
    is_new = 1
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
        'company_org_type':'companyOrgType'
    } 
    
    try:
        if 'establishmentTime' in einfo.keys():
            einfo['establishmentTime'] = format_time(einfo['establishmentTime'])
        "提取企业注册地址省市"
        if 'regLocation' in einfo.keys():
            regLocation = einfo['regLocation']
            if regLocation is not None and regLocation != "":
                reverse_geocoding = get_aff_province_city(regLocation[0:42])
                if reverse_geocoding is not None and reverse_geocoding != "":
                    einfo['province'] = reverse_geocoding['province']
                    einfo['city'] = reverse_geocoding['city']
        "标准化注册资金"
        if 'regCapital' in einfo.keys():
            einfo['reg_capital_standard'] = get_reg_capital_standard(einfo['regCapital'])

        "判断landinn是否存在该企业"
        landinn_aff = query_data(conn,'landinn.affiliations','where is_deleted !=1 and display_name = "' + ename + '" limit 1;')

        "不存在则在landinn新增"
        if landinn_aff.empty:
            aff_id = gen_ticket64(2) 
            einfo['aff_id'] = aff_id
            table = "landinn.affiliations({0})"
            column_str = ','.join([key for key in affiliation_dict])
            value_str = ','.join([format_conversion(einfo.get(affiliation_dict[key])) for key in affiliation_dict])
            table = table.format(column_str,value_str)
            rtn = insert_data(conn,table,"(" + value_str + ")")
            if rtn != 1:
                raise UserMysqlException('插入失败','insert_affiliations','影响行数不为1',str(rtn))
        else:
            "存在则 补充landinn机构信息"
            is_new = 0
            if landinn_aff['is_beihang'][0] == IS_BEIHANG:
                einfo['is_beihang'] = IS_BEIHANG
            else:
                einfo['is_beihang'] = IS_BEIHANG_UPDATE
            aff_id = landinn_aff['affiliation_id'][0]

            set_clause = ''       
            for key in affiliation_dict:
                tyc_key = affiliation_dict.get(key)
                tyc_key_value = format_conversion(einfo.get(tyc_key))
                if not tyc_key_value == 'NULL':
                    set_clause += '{} = {} ,'.format(key,tyc_key_value)

            set_clause += 'affiliation_id = {} where affiliation_id = {} '.format(format_conversion(aff_id),format_conversion(aff_id))
            rtn = update_data(conn,'landinn.affiliations',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('get_landinn_aff_id出错',str(e))
    return aff_id,is_new


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
    "获取注册地址经纬度"
    geoCoding = http_get_geocoding(regLocation)
    if geoCoding:
        longitude = geoCoding['lng']
        latitude = geoCoding['lat']
        "根据经纬度获取省市"
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
        aff_history_name = query_data(conn,'landinn.affiliation_history_name','where is_deleted !=1 and affiliation_id = "' + str(aff_id) + '";')
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
                        value_str += ',({0},{1})'.format(aff_id,format_conversion(his_name)) 
                insert_data(conn,'landinn.affiliation_history_name(affiliation_id,display_name)',re.sub(',', '', value_str, 1))
    except UserMysqlException as e:
        raise UserMysqlException('insert_history_name出错',str(e))


'''
融合作者--操作表 authors 并返回author_id
'''
def get_landinn_author_id(team,aff_id):
    author_dict = {
        'tyc_id':'hid',
        'display_name':'name',
        'title':'title',
        'head_portrait':'icon',
        'brief':'description',
        'last_known_affiliation_id':'aff_id',
        'golaxy_author_id':'author_id' ,
        'is_beihang':'is_beihang'
    }
    team['is_beihang'] = IS_BEIHANG
    
    try:   
        "判断landinn是否存在该作者"
        landinn_author = query_data(conn,'landinn.authors',"where is_deleted !=1 and display_name = {0} and last_known_affiliation_id = {1} {2} ;".format(format_conversion(team['name']),format_conversion(team['aff_id']),'limit 1;'))
        "不存在则在landinn新增"
        if landinn_author.empty:
            author_id = gen_ticket64(2)
            team['author_id'] = author_id
            table = "landinn.authors({0})"
            column_str = ','.join([key for key in author_dict])
            value_str = ','.join([format_conversion(team.get(author_dict[key])) for key in author_dict])
            table = table.format(column_str)
            rtn = insert_data(conn,table,"(" + value_str + ")")
            if rtn != 1:
                raise UserMysqlException('插入失败','insert_authors','影响行数不为1',str(rtn))
        else:
            "存在则进行补充"
            if landinn_author['is_beihang'][0] == IS_BEIHANG:
                team['is_beihang'] = IS_BEIHANG
            else:
                team['is_beihang'] = IS_BEIHANG_UPDATE
            author_id = landinn_author['golaxy_author_id'][0]
            set_clause = ''       
            for key in author_dict:
                tyc_key = author_dict.get(key)
                tyc_key_value = format_conversion(team.get(tyc_key))
                if not tyc_key_value == 'NULL':
                    set_clause += '{} = {} ,'.format(key,tyc_key_value)
            set_clause += 'golaxy_author_id = {} where golaxy_author_id = {} '.format(format_conversion(author_id),format_conversion(author_id))
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
            author_id = get_landinn_author_id(team,aff_id)
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
            tyc_key_value = format_conversion(team.get(tyc_key))
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'author_id = {} where author_id = {} '.format(format_conversion(team['author_id']),format_conversion(team['author_id']))
        rtn = update_data(conn,'landinn.affiliation_team_member',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_team_member出错',str(e))

"增加团队成员"
def insert_landinn_team_member(team,team_dict):
    try:
        table = "landinn.affiliation_team_member({0})"
        column_str = ','.join([key for key in team_dict])
        value_str = ','.join([format_conversion(team.get(team_dict[key])) for key in team_dict])
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
        "根据eid查询核心成员"
        staff_list = query_data(conn,'tianyancha.staff','where eid=' + eid)
        for i,staff in staff_list.iterrows():
            staff['is_beihang'] = IS_BEIHANG
            staff['aff_id'] = aff_id

            if staff['type'] == 1 :
                "机构"
                landinn_sid,aff_new = get_landinn_aff_id({'id':staff['eid'],'name':staff['name'],'is_beihang':staff['is_beihang']})
            else:
                "作者"
                landinn_sid = get_landinn_author_id({'aff_id':aff_id,'hid':staff['sid'],'name':staff['name'],'is_beihang':staff['is_beihang']},aff_id)
            staff['staff_id'] = landinn_sid

            landinn_staff = query_data(conn,"landinn.affiliation_staff","where is_deleted !=1 and staff_id = " + str(landinn_sid) + ";")
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
            tyc_key_value = format_conversion(staff.get(tyc_key))
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)

        set_clause += 'staff_id = {} where staff_id = {} '.format(format_conversion(staff['staff_id']),format_conversion(staff['staff_id']))
        rtn = update_data(conn,'landinn.affiliation_staff',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_staff出错',str(e))
    
"新增staff"
def insert_landinn_staff(staff,staff_dict):
    try:
        table = "landinn.affiliation_staff({0})"
        column_str = ','.join([key for key in staff_dict])
        value_str = ','.join([format_conversion(staff.get(staff_dict[key])) for key in staff_dict])
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
        product_list = query_data(conn,'tianyancha.product','where eid='+eid)

        for i,product in product_list.iterrows():
            product['is_beihang'] = IS_BEIHANG
            product['aff_id'] = aff_id
            product['setupTime'] = format_time(product['setupTime'])

            landinn_product = query_data(conn,"landinn.product","where is_deleted !=1 and tyc_id = " + eid + " and product_name = '" + product['product'] + "';")
            if landinn_product.empty:
                "不存在则新增"
                product_id = gen_ticket64(2)
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
            tyc_key_value = format_conversion(product.get(tyc_key))
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)

        set_clause += 'golaxy_product_id = {} where golaxy_product_id = {} '.format(format_conversion(product['product_id']),format_conversion(product['product_id']))
        rtn = update_data(conn,'landinn.product',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_product出错',str(e))
    
"新增业务"
def insert_landinn_product(product,product_dict):
    try:
        table = "landinn.product({0})"
        column_str = ','.join([key for key in product_dict])
        value_str = ','.join([format_conversion(product.get(product_dict[key])) for key in product_dict])
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
        trademark_list = query_data(conn,'tianyancha.trademark','where eid='+eid)

        for i,trademark in trademark_list.iterrows():
            trademark['aff_id'] = aff_id
            landinn_trademark = query_data(conn,"landinn.trademark","where is_deleted !=1 and tyc_id = " + trademark['id'] + ";")
            if landinn_trademark.empty:
                "不存在则新增"
                trademark['is_beihang'] = IS_BEIHANG
                trademark_id = gen_ticket64(2)
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
            tyc_key_value = format_conversion(trademark.get(tyc_key))
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)

        set_clause += 'golaxy_trademark_id = {} where golaxy_trademark_id = {} '.format(format_conversion(trademark['trademark_id']),format_conversion(trademark['trademark_id']))
        rtn = update_data(conn,'landinn.trademark',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_trademark出错',str(e))

"新增商标"
def insert_landinn_trademark(trademark,trademark_dict):
    try:  
        table = "landinn.trademark({0})"
        column_str = ','.join([key for key in trademark_dict])
        value_str = ','.join([format_conversion(trademark.get(trademark_dict[key])) for key in trademark_dict])
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
        website_list = query_data(conn,'tianyancha.website','where eid='+str(eid))    
        for i,website in website_list.iterrows():
            website['aff_id'] = aff_id       
            "website"
            landinn_website = query_data(conn,"landinn.affiliation_website","where is_deleted !=1 and ym = '" + website['ym'] + "';")
            if landinn_website.empty:
                "不存在则新增" 
                website['website_id'] = gen_ticket64(2)
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
                landinn_website_homepage = query_data(conn,'landinn.affiliation_website_homepage',"where is_deleted !=1 and website_id = '" + str(website_id) + "';")
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
            tyc_key_value = format_conversion(website.get(tyc_key))
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'website_id = {} where website_id = {} '.format(format_conversion(website['website_id']),format_conversion(website['website_id']))
        rtn = update_data(conn,'landinn.affiliation_website',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_website出错',str(e))
            
"新增website"
def insert_landinn_website(website,website_dict):
    try:
        table = "landinn.affiliation_website({0})"
        column_str = ','.join([key for key in website_dict])
        value_str = ','.join([format_conversion(website.get(website_dict[key])) for key in website_dict])
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
        value_str = ','.join([format_conversion(website_homepage[website_homepage_dict[key]]) for key in website_homepage_dict])
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
        landinn_softright = query_data(conn,'landinn.software_copyright','where is_deleted !=1 and tyc_id = "' + softright_id + '" limit 1;') 

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
        value_str = ','.join([format_conversion(softright.get(softright_affiliation_dict[key])) for key in softright_affiliation_dict])
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
            tyc_key_value = format_conversion(softright.get(tyc_key))
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'golaxy_sc_id = {} where golaxy_sc_id = {} '.format(format_conversion(softright['softright_id']),format_conversion(softright['softright_id']))
        rtn = update_data(conn,'landinn.software_copyright',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_softright出错',str(e))
        
"新增软著"
def insert_landinn_softright(softright,softright_dict):
    try:
        softright_id = gen_ticket64(2)
        softright['softright_id'] = softright_id
        table = "landinn.software_copyright({0})"
        column_str = ','.join([key for key in softright_dict])
        value_str = ','.join([format_conversion(softright.get(softright_dict[key])) for key in softright_dict])
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
        patent_list = query_data(conn,'tianyancha.patent','where eid='+str(eid)) 
        num = 0
        for i,patent in patent_list.iterrows(): 
            num += 1
            patent_inventor = patent['inventor']  # tyc发明人 #
            patent_applicationNameList = patent['applicationNameList'] # tyc申请人 #
            # 插入或补全landinn中patent信息，并返回patent_id #
            patent_id = get_landinn_patent_id(patent)
            # 查询landinn专利发明人 #
            patent_authors_list = query_data(conn,'landinn.patent_authors','where is_deleted = 0 and patent_id = '+ str(patent_id) + ' order by author_sequence_number asc')
            if patent_inventor and not patent_inventor.isspace():
                # 规格化tyc专利发明人 #
                patent_inventor = patent_inventor.split(';')
                patent_inventor_list = [i for j,i in zip(range(0,len(patent_inventor)),patent_inventor) if i not in patent_inventor[:j]]
                # 融合专利发明人 #
                merge_patent_author(patent_authors_list,patent_inventor_list,patent_applicationNameList,aff_id,patent_id)
            # 查询专利申请人 #
            patent_applicants_list = query_data(conn,'landinn.patent_applicants','where is_deleted = 0 and patent_id = '+ str(patent_id))
            # 比较天眼和现存landinn申请人数量，不足则补全 #
            if patent_applicationNameList and not patent_applicationNameList.isspace():
                # 规格化tyc专利申请人 #
                list = ast.literal_eval(patent_applicationNameList)
                app_name_list = ';'.join(i for i in list)
                patent_application = app_name_list.split(';')
                patent_application = [i for j,i in zip(range(0,len(patent_application)),patent_application) if i not in patent_application[:j]]
                # 融合专利申请人 #
                merge_patent_application(patent_applicants_list,patent_application,patent_id)            
        log.__exelog__(num,'\n')
    except UserMysqlException as e:
        log.__exelog__(num,'\n')
        raise UserMysqlException('merge_patent出错',str(e))
  
'''
融合专利申请人
'''
def merge_patent_application(patent_applicants_list,patent_application,patent_id):
    try:
        papplicant_dict = {
            'patent_id':'patent_id',
            'applicant_id':'applicant_id',
            'applicant_sequence_number':'seq',
            'original_applicant':'name',
            'applicant_type':'type',
            'is_beihang':'is_beihang' 
        }
        applicant_list = patent_applicants_list.original_applicant # landinn申请人 #
        seq = 0
        for applicant in patent_application:
            seq += 1
            if applicant not in applicant_list.unique():
                # 企业名 #
                if len(applicant) >= 4:
                    # 补充专利申请人 #
                    app_aff_id,is_new = get_landinn_aff_id({'name':applicant})
                    if is_new == 0:
                        continue
                    papplicant = {'patent_id':patent_id,'applicant_id':app_aff_id,'applicant_type':1,'seq':seq,'name':applicant,'is_beihang':IS_BEIHANG}
                    insert_patent_applicants(papplicant,papplicant_dict)
                else:
                    # 人名--按无法确定处理，只修改关系表信息 #
                    author_id = gen_ticket64(2)
                    papplicant = {'patent_id':patent_id,'applicant_id':author_id,'applicant_type':2,'seq':seq,'name':applicant,'is_beihang':IS_BEIHANG}
                    insert_patent_applicants(papplicant,papplicant_dict)
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
        'is_beihang':'is_beihang'
    }
    inventor_list = patent_authors_list.original_author # landinn发明人 #
    seq = 0
    try:
        for inventor in patent_inventor_list:
            seq += 1
            inventor = inventor.strip()
            if inventor.find('其他') >= 0:
                continue
            if inventor.find('不公告设计人') >= 0:
                continue  
            # =1 可确认发明人机构 正常补充发明人#
            if len(patent_applicationNameList) == 1:
                if inventor not in inventor_list.unique():
                    # 补充专利发明人 #
                    author_id = get_landinn_author_id({'aff_id':aff_id,'name':inventor}, aff_id)
                    pauthor = {'patent_id':patent_id,'author_id':author_id,'seq':seq,'name':inventor,'is_beihang':IS_BEIHANG}
                    insert_patent_author(pauthor,patent_author_dict)
            else:
                # 判断该发明人是否存在于landinn中 存在进一步处理 不存在则新增 #
                if inventor in inventor_list.unique():
                    landinn_inventor = patent_authors_list[patent_authors_list['original_author'].isin([inventor])]
                    index = landinn_inventor.index.values[0]
                    landinn_authorId = landinn_inventor.loc[index,'author_id']
                    landinn_isbeihang = landinn_inventor.loc[index,'is_beihang']
                    # 只修改天眼查新增数据，对landinn已存在学者不进行改动 #
                    if landinn_isbeihang == 20101:
                        # 若author表存在该学者 则 修改该作者的 author表 upadted_id #
                        update_20101_author({'author_id':landinn_authorId,'updated_at':str(getNow())})
                        # 修改论文关系表的 author_id 随机序列 #
                        author_id = gen_ticket64(2)
                        pauthor = {'patent_id':patent_id,'author_id':author_id,'seq':seq,'name':inventor,'is_beihang':IS_BEIHANG_UPDATE,'old_author_id':landinn_authorId}
                        update_patent_author(pauthor,patent_author_dict)    
                else:
                    # 补充专利发明人 #
                    author_id = gen_ticket64(2)
                    pauthor = {'patent_id':patent_id,'author_id':author_id,'seq':seq,'name':inventor,'is_beihang':IS_BEIHANG}
                    insert_patent_author(pauthor,patent_author_dict)  
    except UserMysqlException as e:
        raise UserMysqlException('merge_patent_author出错',str(e))

def insert_patent_applicants(papplicant,papplicant_dict):
    "新增专利申请人"
    try:
        table = "landinn.patent_applicants({0})"
        column_str = ','.join([key for key in papplicant_dict])
        value_str = ','.join([format_conversion(papplicant.get(papplicant_dict[key])) for key in papplicant_dict])
        table = table.format(column_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_patent_applicants','影响行数不为1',str(rtn))
    except UserMysqlException as e:
        raise UserMysqlException('insert_patent_applicants出错',str(e))
             
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
            tyc_key_value = format_conversion(author.get(tyc_key))
            set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'golaxy_author_id = {} where golaxy_author_id = {} '.format(format_conversion(author['author_id']),format_conversion(author['author_id']))
        rtn = update_data(conn,'landinn.`authors`',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_20101_author出错',str(e))  

def update_patent_author(pauthor,patent_author_dict):
    "修改专利发明人"
    try:
        set_clause = '' 
        for key in patent_author_dict:
            tyc_key = patent_author_dict.get(key)
            tyc_key_value = format_conversion(pauthor.get(tyc_key))
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'patent_id = {} where patent_id = {} and author_id = {} '.format(format_conversion(pauthor['patent_id']),format_conversion(pauthor['patent_id']),format_conversion(pauthor['old_author_id']))
        rtn = update_data(conn,'landinn.patent_authors',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_patent_author出错',str(e))        
            

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
        landinn_patent = query_data(conn,"landinn.patent","where is_deleted !=1 and publication_number = '" + patent['pubNumber'] + "';")
        "不存在则在landinn新增"
        if landinn_patent.empty: 
            "新增专利"
            patent_id = insert_landinn_patent(patent,patent_dict)
            "新增专利摘要"
            if patent['abstract'] is not None and not patent['abstract'] == "":
                "判断landinn是否存在该专利摘要"
                landinn_patent_abstracts = query_data(conn,"landinn.patent_abstracts","where is_deleted !=1 and patent_id = '" + str(patent_id) + "';")
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
                landinn_patent_abstracts = query_data(conn,"landinn.patent_abstracts","where is_deleted !=1 and patent_id = '" + str(patent_id) + "';")
                if landinn_patent_abstracts.empty:
                    insert_landinn_patent_abstracts(patent)
                else:
                    update_landinn_patent_abstracts(patent)
    except UserMysqlException as e:
        raise UserMysqlException('get_landinn_patent_id出错',str(e))
    return patent_id

    
def update_landinn_patent(patent,patent_dict):
    try:
        set_clause = '' 
        for key in patent_dict:
            tyc_key = patent_dict.get(key)
            tyc_key_value = format_conversion(patent.get(tyc_key))
            if not tyc_key_value == 'NULL':
                set_clause += '{} = {} ,'.format(key,tyc_key_value)
        set_clause += 'golaxy_patent_id = {} where golaxy_patent_id = {} '.format(format_conversion(patent['patent_id']),format_conversion(patent['patent_id']))
        rtn = update_data(conn,'landinn.patent',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_patent出错',str(e))
                     
def insert_landinn_patent_abstracts(patent):  
    try:
        rtn = insert_data(conn,"landinn.patent_abstracts(patent_id,patent_abstract)","(" + format_conversion(patent['patent_id']) + "," + format_conversion(patent['abstract']) + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_landinn_patent_abstracts','影响行数不为1',str(rtn))
    except UserMysqlException as e:
        raise UserMysqlException('insert_landinn_patent_abstracts出错',str(e))

def update_landinn_patent_abstracts(patent):     
    try:
        set_clause = ""    
        set_clause += 'patent_id = {},patent_abstract = {} where patent_id = {} '.format(format_conversion(patent['patent_id']),format_conversion(patent['abstract']),format_conversion(patent['patent_id']))
        rtn = update_data(conn,'landinn.patent_abstracts',set_clause)
    except UserMysqlException as e:
        raise UserMysqlException('update_landinn_patent_abstracts出错',str(e))
               
def insert_landinn_patent(patent,patent_dict):   
    patent_id = gen_ticket64(2) 
    patent['patent_id'] = patent_id    
    try:
        table = "landinn.patent({0})"
        column_str = ','.join([key for key in patent_dict])
        value_str = ','.join([format_conversion(patent.get(patent_dict[key])) for key in patent_dict])
        table = table.format(column_str,value_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_landinn_patent','影响行数不为1',str(rtn)) 
    except UserMysqlException as e:
        raise UserMysqlException('insert_landinn_patent出错',str(e))
    return patent_id


def insert_patent_author(pauthor,patent_author_dict):
    "新增专利发明人"
    pauthor['is_beihang'] = IS_BEIHANG
    try:
        table = "landinn.patent_authors({0})"
        column_str = ','.join([key for key in patent_author_dict])
        value_str = ','.join([format_conversion(pauthor.get(patent_author_dict[key])) for key in patent_author_dict])
        table = table.format(column_str)
        rtn = insert_data(conn,table,"(" + value_str + ")")
        if rtn != 1:
            raise UserMysqlException('插入失败','insert_patent_author','影响行数不为1',str(rtn))   
    except UserMysqlException as e:
        raise UserMysqlException('insert_patent_author出错',str(e))

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
    log.__exelog__('*************************','\n')
    log.__exelog__('本次需融合',execute_times,'批数据','\n')
    log.__exelog__('*************************','\n')
    try:
        for index in range(execute_times):
            conn = pymysql.connect(host = host,port=3306,user = username,passwd = password,charset="utf8")
            mycursor = conn.cursor()
            start_num = temp_num
            temp_num += increment
            print('融合第',index+1,'批企业')
            log.__exelog__('融合第',index+1,'批企业','\n')
            record_df = tyc_to_landinn(lu_time,tu_time,record_df,start_num)

        record_df['last_updated_time'] = [tu_time]
        record_df['execute_complete_time'] = [datetime.datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")]     
        record_df.to_json(expert_file,orient='records',lines=True)
    except UserMysqlException as e:
        raise UserMysqlException('执行有异常','start_execute')     
    return 1
    
    
def tyc_to_landinn(lu_time,tu_time,record_df,start_num):
    
    # 查询天眼查企业数据 -- enterprise  3472906166
    e_list = query_data(conn,"tianyancha.enterprise","where updated_at between '" + str(lu_time) + "' and '" + str(tu_time) + "' limit " + str(start_num) + "," + str(increment) + ";")    
    eid_list = e_list['id']
    ename_list = e_list['name']
    
    print('查询到待融合企业数量：', len(e_list))
    log.__exelog__('查询到待融合企业数量：', len(e_list),'\n')   
    time.sleep(1)
    try :
        # 遍历企业    
        for i,einfo in e_list.iterrows():  
            with tqdm(process, leave=True, ncols=110, bar_format='{l_bar}%s{bar}%s{r_bar}' % (Fore.GREEN, Fore.RESET)) as t:           
                "若天眼查企业名为空则跳过"
                if einfo['name'] is  None or einfo['name'] == "":
                    log.__exelog__('企业',einfo['id'],'该企业数据为空','\n')
                    t.set_description("融合第%i个企业--%s %s "%(i+1,einfo['id'],"该企业数据为空"))
                else:
                    log.__exelog__('融合第',i+1,'个企业：', einfo['name'],'\n')
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
                            log.__exelog__('\t','1. 查询或补全企业','\n')
                            aff_id,aff_new = get_landinn_aff_id(einfo)
                            log.__exelog__('\t\t','1.1. 融合机构历史名称','\n')
                            insert_history_name(aff_id,einfo)
                        if description == '2. 融合核心团队':
                            log.__exelog__('\t','2. 融合核心团队','\n')
                            merge_team_member(eid, aff_id)
                        if description == '3. 融合主要成员':
                            log.__exelog__('\t','3. 融合主要成员','\n')
                            merge_staff(eid, aff_id)
                        if description == '4. 融合业务':
                            log.__exelog__('\t','4. 融合业务','\n')
                            merge_product(eid, aff_id)
                        if description == '5. 融合备案域名':
                            log.__exelog__('\t','5. 融合备案域名','\n')
                            merge_website(eid, aff_id)
                        if description == '6. 融合商标':
                            log.__exelog__('\t','6. 融合商标','\n')
                            merge_trademark(eid, aff_id)
                        if description == '7. 融合软著':
                            log.__exelog__('\t','7. 融合软著','\n')
                            merge_softright(eid, aff_id)
                        if description == '8. 融合专利':
                            log.__exelog__('\t','8. 融合专利','\n')
                            merge_patent(eid,aff_id)
                conn.commit()       
        print('*************************','\n')
        print('所有企业融合完成','\n')
        print('*************************','\n')
        log.__exelog__('*************************','\n')
        log.__exelog__('所有企业融合完成','\n')
        log.__exelog__('*************************','\n')
        return record_df 
    except UserMysqlException as e:       
        log.__errlog__(str(e))
        conn.rollback()
        raise UserMysqlException('执行异常','tyc_to_landinn','程序执行错误')      
    finally:      
        mycursor.close()
        conn.close()

            
if __name__ == '__main__':
    start_execute()
            


# In[ ]:





# In[ ]:





# In[ ]:




