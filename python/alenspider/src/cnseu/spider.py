'''
Created on 2015-12-6

@author: Administrator
'''
import logging
import requests
import re
import uuid

from bs4 import BeautifulSoup
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Topic,Post

request = requests.Session()
request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=1000)
request.mount('http://', adapter)

logfilename = 'cnseu_'+datetime.now().strftime("%Y_%m_%d")+'.log'
logging.basicConfig(name='cnseu',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

engine = create_engine('mysql://root:123456@127.0.0.1/cnseu?use_unicode=0&charset=utf8')

def parse_forum():
    url ='http://www.cnseu.pw/'
    response = request.get(url)
    soup = BeautifulSoup(response.content,'lxml')
    tables = soup.findAll('table',{'class':'fl_tb'})
    for table in tables:
        h2s = table.findAll('h2')
        for h2 in h2s:
            link=h2.a
            print '---------------------------'
            print link.getText().strip()
            print link['href']
            parse_item(link['href'])
            
def parse_total_page(soup):
    totalpage = 1
    ins = soup.find('input',{'name':'custompage'})
    if ins:
        pageinfo = ins.find_next_sibling('span')['title']
        pmatch = re.search('\d+',pageinfo)
        if pmatch:
            totalpage = int(pmatch.group())
    return totalpage

def parse_item(url):
    response = request.get(url)
    soup = BeautifulSoup(response.content,'lxml')
    totalpage = parse_total_page(soup)
    logging.info('------------------parse url---------:\t'+url)
    for i in range(totalpage):
        if i>0:
            purl = url[:-6]+str(i+1)+'.html'
            response = request.get(purl)
            soup = BeautifulSoup(response.content,'lxml')
            logging.info('------------------parse url---------:\t'+purl)
        parse_topic(soup)


def parse_topic(soup):
    tbodies = soup.findAll('tbody',id = re.compile('^stickthread_\d+|^normalthread_\d+'))
    for tbody in tbodies:
        
        Session = sessionmaker()
        Session.configure(bind= engine)
        session = Session()
        
        topicuuid=None
        
        link = tbody.find('a',{'class':'s xst'})
        tid = tbody['id']
        tid = tid[tid.index('_')+1:]
        turl = link['href']
        
        existsrecords = session.query(Topic).filter(Topic.url==turl).filter(Topic.third_party_id==tid).all()
        if existsrecords:
            topicuuid=existsrecords[0].uuid
            logging.info('-----------------exist thread-----------------:\t'+existsrecords[0].third_party_id)
        else:
            created_at = tbody.find('em').span
            if created_at.span:
                created_at = created_at.span['title']
            else:
                created_at = created_at.getText().strip()
            created_at = datetime.strptime(created_at,'%Y-%m-%d')
            
            topicuuid = str(uuid.uuid4())
            name = link.getText().strip()
            
            logging.info('--------------parsing topic:\t'+tid)
            logging.info('third party id:\t'+tid)
            logging.info('name:\t'+name)
            logging.info('url:\t'+turl)
            logging.info('created_at:\t'+str(created_at))
            
            topic = Topic(uuid = topicuuid,name = name,url = turl,third_party_id = tid,forum_uuid = '956a8658-f2ee-1033-858c-7aee3a55fcf1',created_at = created_at)
            session.add(topic)
            session.flush()
            session.commit()
            logging.info('----------------------add thread----------------:\t'+tid)
            
            parse_posts(topicuuid,link['href'])
        
def parse_posts(tid,url):
    response = request.get(url)
    soup = BeautifulSoup(response.content,'lxml')
    totalpage = parse_total_page(soup)
    
    match = re.search('(\w+\-\d+\-)\d+(\-\d+\.html)',url)
    prefix = match.group(1)
    suffix = match.group(2)
    for i in range(totalpage):
        if i>0:
            purl = 'http://www.cnseu.pw/'+prefix+str(i+1)+suffix
            response = request.get(purl)
            soup = BeautifulSoup(response.content,'lxml')
        else:
            purl = url
        logging.info('----------------parsing post at:\t'+purl+'-------------')
    
        posts=[]
        Session = sessionmaker()
        Session.configure(bind= engine)
        session = Session()

        pdivs = soup.findAll('div',id=re.compile('post_\d+'))
        for pdiv in pdivs:
            authdiv = pdiv.find('div',{'class':'authi'})
            pid = pdiv['id'][5:]
            
            postnum = session.query(Post).filter(Post.third_party_id==pid).count()
            if postnum >0:
                logging.info('------------------------exists post--------------:\t'+pid)
            else:
                pbody = pdiv.find('td',id='postmessage_'+pid)
                pdate = pdiv.find('em',id='authorposton'+pid).span
                if pdate:
                    pdate = pdate['title']
                else:
                    pdate = pdiv.find('em',id='authorposton'+pid).getText()[3:].strip()
                logging.info(pdate)
                pdate = datetime.strptime(pdate,'%Y-%m-%d %H:%M:%S')
                pname = authdiv.getText().strip()
                logging.info('----post id:\t'+pid)
                logging.info('----name:\t'+pname)
                logging.info('----date:\t'+str(pdate))
                
                if pbody:
                    logging.info('----body length:\t'+str(len(pbody.getText())))
                    post = Post(uuid = str(uuid.uuid4()),thread_uuid = tid,third_party_id=pid,member_name=pname,body=pbody.getText(),created_at=pdate)
                    posts.append(post)
                    logging.info('--------------add post-------------:\t'+pid)
        if posts:
            session.bulk_save_objects(posts)
            session.flush()
            session.commit()
        session.close()
    

if __name__ == '__main__':
    starttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parse_forum()
#     parse_item('http://www.cnseu.pw/forum-2-1.html')
#     parse_item('http://www.cnseu.pw/forum-38-1.html')
    endtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info('start time:\t'+starttime)
    logging.info('end time:\t'+endtime)