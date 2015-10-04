#-*- coding:utf-8 -*-
'''
Created on 2015-10-2

@author: Administrator
'''
import datetime
import re
import requests
import time
import urlparse
import logging

from bs4 import BeautifulSoup
from threading import Thread
from Queue import Queue

baseurl = 'http://forum.insidepro.com/'

concurrent=6
q = Queue(concurrent*2)

request = requests.Session()
request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=1000)
request.mount('http://', adapter)

logging.basicConfig(name='crackinglog',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

def parse_forum():
    response = request.get(baseurl).content
    soup = BeautifulSoup(response,'lxml')
    links = soup.findAll('a',{'class':'forumlink'})
    for link in links:
        logging.info('+++++++++++++++++++++++++++\t'+link.getText().strip()+'\t++++++++++++++++++++++++++')
        parse_item(urlparse.urljoin(baseurl,link['href']))
        
def parse_total_page(soup):
    
    totalpage = 1
    
    peles = soup.findAll('a',text=re.compile(ur'Next'))
    
    pele = None
    tele = None
    
    if peles:
        pele = peles[0]
        if pele.parent.name == 'b':
            tele = pele.findPrevious('a')
        if tele:
            totalpage = int(tele.text)
        
    return totalpage

def parse_item(url):
    
    soup = BeautifulSoup(request.get(url).content,'lxml')
    
    totalpage = parse_total_page(soup)
    
    for i in range(totalpage):
        itemurl = url+'&topicdays=0&start='+str(i*50)
        q.put(itemurl)
    q.join()
                
def parse_topics(url):
    
    soup = BeautifulSoup(request.get(url).content,'lxml')
    table = soup.find('table',{'class':'forumline'})
    rows = table.findAll('tr')
    postpage = 1
    
    for row in rows:
        td = row.find('td',{'class':'row1','width':'100%'})
        if td:
            topiclinks= td.find('span',{'class':'gensmall'}).findAll('a')
            topicele = td.find('span',{'class':'topictitle'})
            topictitle = topicele.text.strip()
            topiclink = urlparse.urljoin(baseurl,topicele.a['href'])
            if topiclinks:
                postpage = int(topiclinks[len(topiclinks)-1].text)
                logging.info(topiclink+'\t------------------->\t'+topictitle+'\t<--------->\t'+str(postpage))
            else:
                logging.info(topiclink+'\t------------------->\t'+topictitle)
        datespan = row.find('td',{'class':'row3Right'})
        if datespan:
            posttime = time.strptime(datespan.span.contents[0], '%a %b %d, %Y %I:%M %p')
            logging.info('----------last post date:\t'+time.strftime('%Y-%m-%d %H:%M:%S',posttime))
            print '*********************************************************'
            
def dowork():
    while True:
        url = q.get()
        logging.info('+++++++++++++++++++++++++++current url:\t'+url)
        parse_topics(url)
        q.task_done()
        time.sleep(2) 

if __name__ == '__main__':
    starttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for i in range(concurrent):
        t = Thread(target=dowork)
        t.daemon = True
        t.start()
    parse_forum()
    endtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print '********start time:\t',starttime
    print '********end time:\t',endtime