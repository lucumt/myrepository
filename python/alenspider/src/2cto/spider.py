#-*- coding:utf-8 -*-
'''
Created on 2015-11-21

@author: Administrator
'''
import logging
import requests
import re
import time
import uuid

from bs4 import BeautifulSoup
from datetime import datetime
from threading import Thread
from Queue import Queue

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  Column,DateTime,Text,Integer,CHAR,VARCHAR

Base = declarative_base()

class Topic(Base):
    __tablename__ = 'threads'

    tid = Column('id',Integer,primary_key = True)
    uuid = Column('uuid',CHAR(36),unique = True,nullable = False)
    forum_uuid = Column('forum_uuid',CHAR(36),nullable=False,default = '')
    third_party_id = Column('third_party_id',VARCHAR(64),nullable = False,default= '')
    name = Column('name',VARCHAR(255),nullable = False,default = '')
    created_at = Column('created_at',DateTime ,nullable = False)
    url = Column('url',VARCHAR(255),nullable = False,default = '')

    def __init__(self,uuid,forum_uuid,third_party_id,name,created_at,url):
        self.uuid = uuid
        self.forum_uuid = forum_uuid
        self.third_party_id = third_party_id
        self.name = name
        self.created_at = created_at
        self.url = url

    def __repr__(self):
        return "<Metadata('%s','%s','%s','%s','%s','%s','%s')>" % (self.tid,self.uuid,self.forum_uuid,self.third_party_id,self.name,self.created_at,self.url)
    
class Post(Base):
    __tablename__='posts'
    
    pid = Column('id',CHAR(36),primary_key = True)
    uuid = Column('uuid',CHAR(36),unique = True,nullable = False)
    thread_uuid = Column('thread_uuid',CHAR(36), nullable = False)
    third_party_id = Column('third_party_id',VARCHAR(64))
    member_name = Column('member_name',VARCHAR(1000),nullable = False,default = '')
    body = Column('body',Text(),nullable = False)
    created_at = Column('created_at',DateTime,nullable = False)
    
    def __init__(self,uuid,thread_uuid,third_party_id,member_name,body,created_at):
        self.uuid = uuid
        self.thread_uuid = thread_uuid
        self.third_party_id = third_party_id
        self.member_name = member_name
        self.body = body
        self.created_at = created_at
        
    def __repr__(self):
        return "<Metadata('%s','%s','%s','%s','%s','%s','%s')>" % (self.pid,self.uuid,self.thread_uuid,self.third_party_id,self.member_name,self.body,self.created_at)

concurrent=10
q = Queue(concurrent*2)

request = requests.Session()
request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=1000)
request.mount('http://', adapter)

logfilename = '2cto_'+datetime.now().strftime("%Y_%m_%d")+'.log'
logging.basicConfig(name='2cto',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

engine = create_engine('mysql://root:123456@127.0.0.1/2cto?charset=utf8')

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
            Session = sessionmaker()
            Session.configure(bind= engine)
            session = Session()
            topicuuid = str(uuid.uuid4())
            
            tname = link.getText().strip()
            turl = 'http://bbs.2cto.com/'+link['href']
            t_party_id = link['id'][7:]
            created_td = td.parent.find('td',{'class':'author'})
            t_created_at = created_td.p.getText().strip()
            t_last_update = created_td.find_next_sibling('td',{'class':'author'}).p.a['title']
            t_created_at= datetime.strptime(t_created_at,'%Y-%m-%d')
            t_last_update= datetime.strptime(t_last_update,'%Y-%m-%d %H:%M')
            logging.info('------------------------------------------')
            logging.info('name:\t'+tname)
            logging.info('third party id:\t'+t_party_id)
            logging.info('url:\t'+turl)
            logging.info('created at:\t'+str(t_created_at))
            logging.info('last update:\t'+str(t_last_update))
            topic = Topic(uuid = topicuuid,name = tname,url = turl,third_party_id = t_party_id,forum_uuid = '9f6c5c53-e995-1033-a072-e7fc3b303faa',created_at = t_created_at)
            logging.info('----------------------add thread----------------:\t'+t_party_id)
            session.add(topic)
            session.commit()
            session.close()
            parse_posts(topicuuid,turl)
            
            
def parse_posts(topicuuid,url):
    response = request.get(url)
    soup = BeautifulSoup(response.content,'html.parser')
    totalpage = parse_total_page(soup)
    for i in range(totalpage):
        Session = sessionmaker()
        Session.configure(bind= engine)
        session = Session()
        posts=[]
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
            pid=pdiv['id'][10:]
            if not pdate:
                continue
            else:
                pdate=datetime.strptime(pdate['title'],'%Y-%m-%d %H:%M:%S')
            logging.info('pid:\t'+pdiv['id'][10:])
            logging.info('member name:\t'+pname)
            logging.info('body:\t'+str(len(pbody)))
            logging.info('pdate:\t'+str(pdate))
            post = Post(uuid = str(uuid.uuid4()),thread_uuid = topicuuid,third_party_id=pid,member_name=pname,body=pbody,created_at=pdate)
            posts.append(post)
            logging.info('----------------------add post----------------:\t'+pid)
        if posts:
            session.bulk_save_objects(posts)
            session.flush()
            session.commit()
        session.close()
            
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