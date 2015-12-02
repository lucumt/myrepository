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
from datetime import datetime,timedelta
from threading import Thread
from Queue import Queue

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Topic,Post

currentday = datetime.now().strftime("%d-%m-%Y")
yesterday=(datetime.now()-timedelta(days=1)).strftime("%d-%m-%Y")


concurrent=10
q = Queue(concurrent*2)

request = requests.Session()
request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=1000)
request.mount('http://', adapter)

logfilename = 'carderpro_'+datetime.now().strftime("%Y_%m_%d")+'.log'
logging.basicConfig(name='carderpro',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

engine = create_engine('mysql://root:123456@127.0.0.1/carderpro?use_unicode=0&charset=utf8')

def parse_forum():
    url = 'http://verified.bz/'
    
    fpattern ='forumdisplay\.php\?s=\w+&(f=\d+)'
    
    response = request.get(url)
    soup = BeautifulSoup(response.content,'lxml')
    tds = soup.findAll('td',{'class':'alt1Active'})
    index = 0
    for td in tds:
        link = td.findAll('a')[0]['href']
        match = re.search(fpattern,link)
        if match:
            link='http://verified.bz/forumdisplay.php?'+match.group(1)
            index = index+1
            parse_item(link)

def parse_item(url):
    content = request.get(url+'&order=desc&page=1').content
    soup = BeautifulSoup(content,'lxml')
    totalpage = parse_total_page(soup)
    for i in range(totalpage):
        itemurl = url+'&order=desc&page='+str(i+1)
        if i>0:
            response = request.get(itemurl).content
            soup=BeautifulSoup(response,'lxml')
        q.put(soup)
    q.join()

def parse_total_page(pagediv):
    totalpage = 1
    pmatch = re.search('Page\s\d+ of\s(\d+)',pagediv.getText())
    if pmatch:
        totalpage = int(pmatch.group(1))
    return totalpage
    
    
def parse_topic(soup):
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
                    date = tr.findAll('td')[3].getText().strip()
                    if date == '-':
                        lastpostdate=datetime.fromtimestamp(0)
                    else:
                        lastpostdate=date[:19]
                        if 'Today' in lastpostdate:
                            lastpostdate=lastpostdate[:14].strip()
                            lastpostdate=lastpostdate.replace('Today',currentday)
                        elif 'Yesterday' in lastpostdate :
                            lastpostdate=lastpostdate[:18].strip()
                            lastpostdate=lastpostdate.replace('Yesterday',yesterday)
                        lastpostdate=lastpostdate.replace('\n','')
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

def parse_post(url,topicuuid):
    
    content = request.get(url).content
    totalpage = 1
    
    soup = BeautifulSoup(content,'lxml')
    pdiv = soup.find('div',{'class':'pagenav'})
    if pdiv:
        totalpage = parse_total_page(pdiv)
    for i in range(totalpage,0,-1):
#         time.sleep(3)
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
            postnum = session.query(Post).filter(Post.third_party_id==thirdpartyid).count()
            if postnum >0:
                logging.info('------------------------exists post--------------:\t'+thirdpartyid)
            else:
                membername = table.find('a',{'class':'bigusername'})
                if not membername:
                    membername=table.find('div',id='postmenu_'+thirdpartyid)
                membername=membername.getText().strip()
                postdate=table.find('a',{'name':'post'+thirdpartyid}).parent.getText().strip()
                if 'Today' in postdate:
                    postdate=postdate.replace('Today',currentday)
                elif 'Yesterday' in postdate :
                    postdate=postdate.replace('Yesterday',yesterday)
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

def dowork():
    while True:
        soup = q.get()
        parse_topic(soup)
        q.task_done()
        time.sleep(2) 

if __name__ == '__main__':
    starttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for i in range(concurrent):
        t = Thread(target=dowork)
        t.daemon = True
        t.start()
    parse_forum()
    #parse_topic('http://verified.bz/forumdisplay.php?f=162')
    endtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info('start time:\t'+starttime)
    logging.info('end time:\t'+endtime)