#-*-coding:utf-8-*-
'''
Created on 2015-10-25

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

from models import Topic,Post

concurrent=10
q = Queue(concurrent*2)

request = requests.Session()
request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=1000)
request.mount('http://', adapter)

logfilename = 'lampeduza_'+datetime.now().strftime("%Y_%m_%d")+'.log'
logging.basicConfig(name='inlampeduza',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

engine = create_engine('mysql://root:123456@127.0.0.1/lampeduza?charset=utf8')

def parse_lampeduza():
    url = 'https://lampeduza.so/'
    response = request.get(url).content
    soup = BeautifulSoup(response,'lxml')
    tds = soup.findAll('td',{'class':'col_c_forum'})
    for td in tds:
        link = td.h4.strong.a
        if check_access(link['href']):
            parse_item(link['href'])
        
def check_access(url):
    response = request.get(url).content
    if "Sorry, we couldn't find that!" not in response:
        return True
    else:
        return False

def parse_total_page(soup):
    totalpage = 1
    pageli = soup.find('li',{'class':'pagejump'})
    if pageli:
        pageinfo=pageli.a.getText().strip()
        match = re.search('Page\s\d+ of\s(\d+)', pageinfo)
        if match:
            totalpage = int(match.group(1))
    return totalpage    

def parse_item(url):
    response = request.get(url).content
    soup = BeautifulSoup(response,'lxml')
    totalpage = parse_total_page(soup)
    for i in range(totalpage):
        topicurl=url+'page-'+str(i+1)+'?prune_day=100&sort_by=Z-A&sort_key=last_post&topicfilter=all'
        logging.info('----------------Begin to parse url------------:\t'+topicurl)
        if i>0:
            response = request.get(topicurl).content
            soup=BeautifulSoup(response,'lxml')
        q.put(soup)
    q.join()

def parse_topics(soup):
    tds = soup.findAll('td',{'class':'col_f_content'})
    for td in tds:
        link = td.h4.a
        linkinfos=link['title'].split('- started')
        
        topicurl = link['href']
        name=linkinfos[0].strip()
        thirdpartyid=link['id'].strip()[9:]
        topicuuid=None
        
        Session = sessionmaker()
        Session.configure(bind= engine)
        session = Session()
        
        existsrecords = session.query(Topic).filter(Topic.url==topicurl).filter(Topic.third_party_id==thirdpartyid).all()
        if existsrecords:
            topicuuid= existsrecords[0].uuid
            logging.info('-------------------exists thread----------------:\t'+existsrecords[0].third_party_id)
        else:
            logging.info('-------------------create thread----------------:\t'+thirdpartyid)
            logging.info('third party id:\t'+thirdpartyid)
            logging.info('name:\t'+name)
            logging.info('url:\t'+topicurl)
            if linkinfos[1].strip() !='--':
                createdat=datetime.strptime(linkinfos[1].strip(),'%d %B %Y - %I:%M %p')
                logging.info('created_at:\t'+str(createdat))
            else:
                createdat=datetime.fromtimestamp(0)
            topicuuid = str(uuid.uuid4()) 
            topic = Topic(uuid = topicuuid,name = name,url = topicurl,third_party_id = thirdpartyid,forum_uuid = 'ba4e11e1-6b90-11e5-9db3-0cc47a34a45a',created_at = createdat)
            session.add(topic)
            session.flush()
            session.commit()
        session.close()
        parse_posts(topicurl,topicuuid)
            
def parse_posts(url,topicuuid):
    time.sleep(5)
    response=requests.get(url).content
    soup = BeautifulSoup(response)
    totalpage=parse_total_page(soup)
    for i in range(totalpage):
        posturl=url+'page-'+str(i+1)
        if i>0:
            response=requests.get(posturl).content
            soup = BeautifulSoup(response)
        posts=soup.findAll('div',{'class':'post_block'})
        
        postlist = []
        Session = sessionmaker()
        Session.configure(bind= engine)
        session = Session()
        
        for post in posts:
            pname = post.find('div',{'class':'post_username'}).getText().strip()
            thirdpartyid=post['id'][8:]
            
            postnum = session.query(Post).filter(Post.third_party_id==thirdpartyid).filter(Post.member_name==pname).count()
            
            if postnum>0:
                logging.info('------------------------exists post--------------:\t'+thirdpartyid)
            else:
                pdate = post.find('div',{'class':'post_date'}).abbr['title']
                pdate = datetime.strptime(pdate,'%Y-%m-%dT%H:%M:%S+00:00')
                body = post.find('div',{'class':'post_body'}).div.getText().strip()
            
                logging.info('------------create posts-------------:\t'+thirdpartyid)
                logging.info('Third party id:\t'+thirdpartyid)
                logging.info('Member name:\t'+pname)
                logging.info('Created date:\t'+str(pdate))
                logging.info('Post body length:\t'+str(len(body)))
                
                post = Post(uuid = str(uuid.uuid4()),thread_uuid = topicuuid,third_party_id=thirdpartyid,member_name=pname,body=body,created_at=pdate)
                postlist.append(post)
        if postlist:
            session.bulk_save_objects(postlist)
            session.flush()
            session.commit()
        session.close()
        
def dowork():
    while True:
        soup = q.get()
        parse_topics(soup)
        q.task_done()
        time.sleep(2) 

if __name__ == '__main__':
    starttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for i in range(concurrent):
        t = Thread(target=dowork)
        t.daemon = True
        t.start()
    parse_lampeduza()
    endtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info('start time:\t'+starttime)
    logging.info('end time:\t'+endtime)