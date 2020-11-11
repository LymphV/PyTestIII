# *-* coding:utf-8 *-*  
import requests  
from bs4 import BeautifulSoup  
import lxml  
from multiprocessing import Process, Queue  
import random  
import json  
import time  
import requests  
from lxml import etree
 
class Proxies(object):  
  
  
    """docstring for Proxies"""  
    def __init__(self, page=30):  
        self.proxies = []  
        self.verify_pro = []  
        self.page = page  
        self.headers = {  
        'Accept': '*/*',  
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',  
        'Accept-Encoding': 'gzip, deflate, sdch',  
        'Accept-Language': 'zh-CN,zh;q=0.8' ,
        'Connection': 'close',
        }  
        self.get_proxies()  

  
    def get_proxies(self):  
        page = 1# random.randint(1,10)  
        page_stop = page + self.page  
        while page < page_stop: 
            url =  'http://www.89ip.cn/index_%d.html'  % page  
            html = requests.get(url, headers=self.headers).content  
            time.sleep(1)
            selector=etree.HTML(html)  
            IPList=selector.xpath("//*[@class='layui-table']//td[1]/text()")
            IPList=[ip.strip()  for ip in IPList]
            PortList=selector.xpath("//*[@class='layui-table']//td[2]/text()")
            PortList=[Port.strip()  for Port in PortList]
            #ProtocalList=selector.xpath("//*[@data-title='类型']/text()")
            self.proxies.extend( ["http"+"://"+IPList[i]+":"+PortList[i] for i in range(len(IPList))])  
            page += 1  

    def verify_proxies(self):  
        # 没验证的代理  
        old_queue = Queue()  
        # 验证后的代理  
        new_queue = Queue()  
        print ('verify proxy........')  
        works = []  
        for _ in range(15):  
            works.append(Process(target=self.verify_one_proxy, args=(old_queue,new_queue)))  
        for work in works:  
            work.start()  
        for proxy in self.proxies:  
            old_queue.put(proxy)  
        for work in works:  
            old_queue.put(0)  
        for work in works:  
            work.join()  
        self.proxies = []  
        print("while 1")
        while 1:  
            try:  
                self.proxies.append(new_queue.get(timeout=1))  
            except:  
                break  
        print ('verify_proxies done!')  
  
  
    def verify_one_proxy(self, old_queue, new_queue):  
        while 1:  
            proxy = old_queue.get()  
            if proxy == 0:break  
            protocol = 'https' if 'https' in proxy else 'http'  
            proxies = {protocol: proxy}  
            try:
                time.sleep(0.5)  
                if requests.get('http://patft.uspto.gov/netahtml/PTO/search-bool.html', proxies=proxies, timeout=5).status_code == 200:  
                    print ('success %s' % proxy)  
                    new_queue.put(proxy)  
            except:  
                print ('fail %s' % proxy)  
  
  
if __name__ == '__main__':  
    a = Proxies()  
    a.verify_proxies()  
    print (a.proxies)  
    proxie = a.proxies   
    with open('proxies.txt', 'w') as f:  
       for proxy in proxie:  
             f.write(proxy+'\n')  