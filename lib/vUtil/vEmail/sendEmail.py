'''
发送邮件

==========

sendEmail(content, subject, receiver) 发送邮件
'''
import smtplib
from email.mime.text import MIMEText
from email.header import Header

from datetime import datetime, timedelta, timezone

host="smtp.163.com"  #设置服务器
user="pyLymphV"    #用户名
password="GDSJXWEJZKNNNHNA"   #口令 

sender = 'pyLymphV@163.com'

tz = timezone(timedelta(hours=8))
graduation = datetime(2022,7,1,tzinfo=tz)

def sendEmail (content = 'test', subject = 'hello there', receiver = '470481777@qq.com'):
    '''
    发送邮件
    
    Parameters
    ----------
    content : 邮件内容
    subject : 邮件主题
    receiver : 接收者，暂不可列表
    '''
    
    ### 防止毕业后仍然收到邮件
    if graduation < datetime.now(tz): return

    
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = sender
    message['To'] =  receiver
    message['Subject'] = Header(subject, 'utf-8')
    
    smtpObj = smtplib.SMTP() 
    smtpObj.connect(host, 25)    # 25 为 SMTP 端口号
    smtpObj.login(user,password)
    
    smtpObj.sendmail(sender, [receiver], message.as_string())
    
    smtpObj.close()