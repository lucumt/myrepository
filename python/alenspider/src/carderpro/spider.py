#-*- coding:utf-8 -*-
'''
Created on 2015-11-7

@author: Administrator
'''
import requests
import re
import logging
import time
import uuid

from bs4 import BeautifulSoup
from datetime import datetime
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
    member_name = Column('member_name',VARCHAR(64),nullable = False,default = '')
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


request = requests.Session()
request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=1000)
request.mount('http://', adapter)

logfilename = 'carderpro_'+datetime.now().strftime("%Y_%m_%d")+'.log'
logging.basicConfig(name='carderpro',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S',filename=logfilename)

engine = create_engine('mysql://root:123456@127.0.0.1/carderpro?charset=utf8')

def parse_forum():
    url = 'http://verified.bz/'
    
    fpattern ='forumdisplay\.php\?s=\w+&(f=\d+)'
    
    response = request.get(url)
    soup = BeautifulSoup(response.content,'lxml')
    tds = soup.findAll('td',{'class':'alt1Active'})
    for td in tds:
        link = td.findAll('a')[0]['href']
        match = re.search(fpattern,link)
        if match:
            link='http://verified.bz/forumdisplay.php?'+match.group(1)
            parse_topic(link)
            logging.info('------------------------------------------------')

def check_authority(content):
    if 'Your administrator has required a password to access this forum. Please enter this password now.' in content:
        return False
    else:
        return True

def parse_total_page(pagediv):
    totalpage = 1
    pmatch = re.search('Page\s\d+ of\s(\d+)',pagediv.getText())
    if pmatch:
        totalpage = int(pmatch.group(1))
    return totalpage
    
    
def parse_topic(url):
    content = request.get(url+'&order=desc&page=1').content
    if not check_authority(content):
        return
    soup = BeautifulSoup(content,'lxml')
    
    totalpage = 1
    pagediv = soup.find('div',{'class':'pagenav'})
    if pagediv:
        totalpage = parse_total_page(pagediv)
    for i in range(totalpage):
        time.sleep(3)
        if i>0:
            itemurl = url+'&order=desc&page='+str(i+1)
            purl=itemurl
            content = request.get(itemurl).content
            soup = BeautifulSoup(content,'lxml')
        else:
            purl=url
        tbody = soup.find('tbody',id=re.compile('^threadbits_forum_\d+'))
        if tbody:
            trs = tbody.findAll('tr')
            for tr in trs:
                
                topicuuid=None
                
                link = tr.find('a',id=re.compile('^thread_title_\d+'))
                if link:
                    
                    Session = sessionmaker()
                    Session.configure(bind= engine)
                    session = Session()
                    
                    thirdpartyid=link['id'][13:]
                    turl =link['href']
                    tmatch = re.search('showthread.php\?s=\w+&(t=\d+)',turl)
                    if tmatch:
                        turl = 'http://verified.bz/showthread.php?'+tmatch.group(1)
                    else:
                        turl = 'http://verified.bz/'+turl
                     
                    existsrecords = session.query(Topic).filter(Topic.url==turl).filter(Topic.third_party_id==thirdpartyid).all()
                    if existsrecords:
                        topicuuid=existsrecords[0].uuid
                        logging.info('-----------------exist thread-----------------:\t'+existsrecords[0].third_party_id)
                    else:
                        topicuuid=str(uuid.uuid4())
                        date = tr.findAll('td')[3]
                        lastpostdate=date.getText().strip()[:19]
                        lastpostdate=datetime.strptime(lastpostdate,'%d-%m-%Y %I:%M %p')
                        name=link.getText().strip()
                        
                        logging.info('name:\t'+name)
                        logging.info('url:\t'+turl)
                        logging.info('third party id:\t'+thirdpartyid)
                        logging.info('date:\t'+str(lastpostdate))
                        topic = Topic(uuid = topicuuid,name = name,url = turl,third_party_id = thirdpartyid,forum_uuid = '3861fa39-83d1-11e5-9db3-0cc47a34a45a',created_at = lastpostdate)
                        session.add(topic)
                        session.flush()
                        session.commit()
                        logging.info('----------------------add thread----------------:\t'+thirdpartyid)
                    session.close()
                    parse_post(turl,topicuuid)
        logging.info('***************************finished parsing topic*********************:\t'+purl)

def parse_post(url,topicuuid):
    
    content = request.get(url).content
    totalpage = 1
    
    soup = BeautifulSoup(content,'lxml')
    pdiv = soup.find('div',{'class':'pagenav'})
    if pdiv:
        totalpage = parse_total_page(pdiv)
    for i in range(totalpage,0,-1):
        time.sleep(3)
        posturl=url+'&page='+str(i)
        if i==1:
            psoup=soup
        else:
            content = request.get(posturl).content
            psoup = BeautifulSoup(content,'lxml')
        tables = psoup.findAll('table',id=re.compile('^post\d+'))
        logging.info('--------------parsing post for url:\t'+posturl)
        
        posts=[]
        Session = sessionmaker()
        Session.configure(bind= engine)
        session = Session()
         
        for table in tables:
            thirdpartyid=table['id'][4:]
            membername = table.find('a',{'class':'bigusername'})
            if not membername:
                membername=table.find('div',id='postmenu_'+thirdpartyid)
            membername=membername.getText().strip()
            postdate=table.find('a',{'name':'post'+thirdpartyid}).parent.getText().strip()
            postdate=datetime.strptime(postdate,'%d-%m-%Y, %I:%M %p')
            body=table.find('td',id='td_post_'+thirdpartyid).getText().strip()
            logging.info('member name:\t'+membername)
            logging.info('third party id:\t'+thirdpartyid)
            logging.info('post date:\t'+str(postdate))
            logging.info('post body length:\t'+str(len(body)))
            logging.info('--------------add post-------------:\t'+thirdpartyid)
            post = Post(uuid = str(uuid.uuid4()),thread_uuid = topicuuid,third_party_id=thirdpartyid,member_name=membername,body=body,created_at=postdate)
            posts.append(post)
        if posts:
            session.bulk_save_objects(posts)
            session.flush()
            session.commit()
        session.close()

if __name__ == '__main__':
    starttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parse_forum()
#     url='http://verified.bz/forumdisplay.php?f=201'
#     parse_topic(url)
#     parse_post('http://verified.bz/showthread.php?t=42077',str(uuid.uuid4()))
#     parse_post('http://verified.bz/showthread.php?t=8635')
    endtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info('start time:\t'+starttime)
    logging.info('end time:\t'+endtime)