#-*- coding:utf-8 -*-
'''
Created on 2015-10-2

@author: Administrator
'''
import re
import requests
import time
import urlparse
import uuid
import logging

from bs4 import BeautifulSoup
from threading import Thread
from Queue import Queue
from datetime import datetime,timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Topic

baseurl = 'http://forum.insidepro.com/'

concurrent=6
q = Queue(concurrent*2)

request = requests.Session()
request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=1000)
request.mount('http://', adapter)

logging.basicConfig(name='crackinglog',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

insidepostpattern = re.compile(ur'^Posted:(.*?)Post subject:')

engine = create_engine('mysql://root:123456@127.0.0.1/insidepro?charset=utf8')

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
    
    Session = sessionmaker()
    Session.configure(bind= engine)
    session = Session()
    
    urls = []
    topics = []
    topic = None
    
    lastposttimestr = None
    lastposttime = None
    name = None
    topicurl = None
    thirdpartyid = None
    
    for row in rows:
        td = row.find('td',{'class':'row1','width':'100%'})
        if td:
            topiclinks= td.find('span',{'class':'gensmall'}).findAll('a')
            topicele = td.find('span',{'class':'topictitle'})
            name = topicele.text.strip()
            topicurl = urlparse.urljoin(baseurl,topicele.a['href'])
            
            parameters = urlparse.parse_qs(urlparse.urlparse(topicurl).query)
            thirdpartyid = parameters['t'][0]
            
            if topiclinks:
                postpage = int(topiclinks[len(topiclinks)-1].text)
                logging.info(topicurl+'\t------------------->\t'+thirdpartyid+'\t---->\t'+name+'\t<--------->\t'+str(postpage))
            else:
                logging.info(topicurl+'\t------------------->\t'+parameters['t'][0]+'\t---->\t'+name)
            datespan = row.find('td',{'class':'row3Right'})
            if datespan:
                lastposttimestr = datespan.span.contents[0]
                lastposttime = datetime.strptime(lastposttimestr,'%a %b %d, %Y %I:%S %p')
                logging.info('last post date:\t'+lastposttimestr)
                logging.info('*********************************************************')
            existsrecords = session.query(Topic).filter(Topic.url==topicurl).all()
            if topicurl not in urls:
                if not existsrecords:
                    topic = Topic(uuid=str(uuid.uuid4()),name=name,url=topicurl,third_party_id=thirdpartyid,forum_uuid='',created_at=lastposttime)
                    topics.append(topic)
                    urls.append(topicurl)
                    parse_post(topicurl, postpage)
                elif existsrecords[0].created_at < datetime.now()-timedelta(days=1):
                    parse_post(topicurl,postpage)
            
    session.bulk_save_objects(topics)
    session.flush()
    session.commit()

def parse_post(url,totalpage):
    
    for i in range(totalpage):
        posturl = url+'&postdays=0&postorder=desc&'+str(i*15)
        response = request.get(posturl).content
        soup = BeautifulSoup(response,'lxml')
        spans = soup.findAll('span',{'class':'name'})
        for span in spans:
            dataele = span.parent.findNextSibling('td')
            postinfo = dataele.find('span',{'class':'postdetails'}).text.strip()
            body = dataele.find('span',{'class':'postbody'}).text.strip()
            logging.info('member name:\t'+span.b.text.strip())
            logging.info('post time:\t'+insidepostpattern.match(postinfo).group(1).strip())
            logging.info(body)
            logging.info('----------------------------------------')
            
def dowork():
    while True:
        url = q.get()
        logging.info('+++++++++++++++++++++++++++current url:\t'+url)
        parse_topics(url)
        q.task_done()
        time.sleep(2) 

if __name__ == '__main__':
    starttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for i in range(concurrent):
        t = Thread(target=dowork)
        t.daemon = True
        t.start()
    parse_forum()
    endtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print '********start time:\t',starttime
    print '********end time:\t',endtime