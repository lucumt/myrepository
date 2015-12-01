#-*- coding:utf-8 -*-
'''
Created on 2015-11-21

@author: Administrator
'''
import logging
import requests
import re
import time

from bs4 import BeautifulSoup
from datetime import datetime
from threading import Thread
from Queue import Queue

concurrent=10
q = Queue(concurrent*2)

request = requests.Session()
request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=1000)
request.mount('http://', adapter)

logfilename = '2cto_'+datetime.now().strftime("%Y_%m_%d")+'.log'
logging.basicConfig(name='2cto',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

def parse_forum():
    url = 'http://bbs.2cto.com/'
    response = request.get(url)
    soup = BeautifulSoup(response.content,'html.parser')
    trs = soup.findAll('tr',{'class':'tr3'})
    for tr in trs:
        link = tr.th.h2.a
        print '-------------------'
        logging.info(link.getText().strip()+'\t'+link['href'])
        parse_item('http://bbs.2cto.com/'+link['href'])

def parse_total_page(soup):
    totalpage = 1
    nextlink = soup.find('a',{'class':'pages_next'})
    if nextlink:
        previouslink = nextlink.previous_sibling
        if previouslink:
            linkcontent = previouslink.getText().strip()
            match = re.search('\d+',linkcontent)
            totalpage = match.group()
    else:
        pagediv = soup.find('div',{'class':'pages'})
        if pagediv:
            links = pagediv.findAll('a')
            last_link = None
            for last_link in links:pass
            if last_link:
                totalpage = last_link.getText().strip()
    return int(totalpage)    
    
def parse_item(url):
    response = request.get(url)
    soup = BeautifulSoup(response.content,'html.parser')
    totalpage = parse_total_page(soup)
    for i in range(totalpage):
#         if i>0:
#             break;
        topicurl = url+'&page='+str(i+1)
        logging.info('+++++++++++++++++++++++++++++++++++++topicurl:\t'+topicurl)
        time.sleep(2)
        q.put(topicurl)
    q.join()

def parse_topic(url):
    response = request.get(url)
    soup = BeautifulSoup(response.content,'html.parser')
    tds = soup.findAll('td',{'class':'subject'})
    for td in tds:
        link = td.find('a',{'class':'subject_t f14'})
        if link:
            tname = link.getText().strip()
            turl = 'http://bbs.2cto.com/'+link['href']
            t_party_id = link['id'][7:]
            t_created_at = td.parent.find('td',{'class':'author'}).p.getText().strip()
            logging.info('------------------------------------------')
            logging.info('name:\t'+tname)
            logging.info('third party id:\t'+t_party_id)
            logging.info('url:\t'+turl)
            logging.info('created at:\t'+t_created_at)
#             print td.find_next_sibling('td')
#         createele = 
            parse_posts(turl)
            
def parse_posts(url):
    response = request.get(url)
    soup = BeautifulSoup(response.content,'html.parser')
    totalpage = parse_total_page(soup)
    for i in range(totalpage):
        if i>0:
            purl = url+'&page='+str(i+1)
            response = request.get(purl)
            soup = BeautifulSoup(response.content,'html.parser')
            logging.info('----------------------Parsing post page:\t'+purl)
        else:
            logging.info('----------------------Parsing post page:\t'+url+'&page=1')
        pdivs = soup.findAll('div',{'class':'read_t'})
        for pdiv in pdivs:
            pname = pdiv.find('div',{'class':'readName'}).getText().strip()
            pbody = pdiv.find('div',{'class':'tpc_content'}).getText().strip()
            pdate = pdiv.find('span',text = re.compile(unicode(u'发表于')))
            if not pdate:
                continue
            logging.info('pid:\t'+pdiv['id'][10:])
            logging.info('member name:\t'+pname)
            logging.info('body:\t'+pbody)
            logging.info('pdate:\t'+pdate['title'])
            
def dowork():
    while True:
        url = q.get()
        parse_topic(url)
        q.task_done()
        time.sleep(2) 

if __name__ == '__main__':
    starttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for i in range(concurrent):
        t = Thread(target=dowork)
        t.daemon = True
        t.start()
    parse_forum()
#     parse_posts('http://bbs.2cto.com/read.php?tid=371985')
#     parse_posts('http://bbs.2cto.com/read.php?tid=371258')
#     parse_posts('http://bbs.2cto.com/read.php?tid=372526')
#     parse_posts('http://bbs.2cto.com/read.php?tid=310778&fpage=84')
#     parse_posts('http://bbs.2cto.com/read.php?tid=187091&fpage=158&page=1')
#     parse_item('http://bbs.2cto.com/thread.php?fid=49')
    endtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info('start time:\t'+starttime)
    logging.info('end time:\t'+endtime)