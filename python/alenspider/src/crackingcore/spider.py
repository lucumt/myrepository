#-*- coding:utf-8 -*-
'''
Created on 2015-9-25

@author: Administrator
'''
import requests
import re
import uuid
import logging
import time
import traceback
import sys

from bs4 import BeautifulSoup
from datetime import datetime
from threading import Thread
from Queue import Queue
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

from models import Topic,Post

crackconcurrent=10
crackq = Queue(crackconcurrent*2)

#logfilename = 'crackingcore_'+sys.argv[1]+'_'+datetime.now().strftime("%Y_%m_%d")+'.log'
logging.basicConfig(name='crackinglog',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

request = requests.Session()
request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.26'
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
request.mount('http://', adapter)
  
engine = create_engine('mysql://root:123456@127.0.0.1/crackingcore?charset=utf8')  # 定义引擎 

crackingpattern = re.compile('http://www.crackingcore.com/topic/(\d+)\-')
currentday = datetime.now().strftime("%b %d %Y")

def parse_totalpage(url):
    soup = BeautifulSoup(request.get(url).content,'html.parser')
    totalpage = 1
    pageinfo = soup.find('a',{'href':'#'})
    if pageinfo:#have more than one page
        pageinfo = pageinfo.getText()
        match = re.search('Page\s\d+ of\s(\d+)', pageinfo)
        if match:
            totalpage = int(match.group(1))
    return totalpage

def parse_module():
    response = request.get('http://www.crackingcore.com/',allow_redirects=True)
    soup = BeautifulSoup(response.content,'html.parser')
    
    #parse information
    eles = soup.findAll('div', id=re.compile('^category_\d+'))
    for ele in eles:
        itemid = ele['id']
        if sys.argv[1] =='front':
            items=['category_1','category_5','category_10','category_67']
        else:
            items=['category_154','category_15']
        #if itemid in['category_1','category_5','category_67','category_10','category_154','category_15']:
        if itemid in items:
            items = soup.find('div',id = itemid).findAll('h4',{'class':'forum_name'})
            for item in items:
                url = item.strong.a['href']
                   
                #parse topic for submodule
                parse_subforum_topic(url)
                   
                #get the total page of each subitem
                totalpage = parse_totalpage(url)
                   
                #parse topic in each page       
                for i in range(totalpage,0,-1):
                    posturl = url+'page-'+str(i)+'?prune_day=100&sort_by=Z-A&sort_key=last_post&topicfilter=all'
                    crackq.put(posturl)
            crackq.join()
            
    
def parse_subforum_topic(url):
    soup = BeautifulSoup(request.get(url).content,'html.parser')
    links = soup.findAll('div',{'class':'f_name'})
    if links:
        logging.info("**************begin to parse submodule for*************")
        for link in links:
            url = link.find('a')['href'].strip()
            totalpage = parse_totalpage(url)
            for i in range(totalpage,0,-1):
                posturl = url+'page-'+str(i)+'?prune_day=100&sort_by=Z-A&sort_key=last_post&topicfilter=all'
                crackq.put(posturl)

def parse_topics(url):
    logging.info('-------------------parsing page:%s',url)
    soup2 = BeautifulSoup(request.get(url).content,'html.parser')
    topics = soup2.findAll('tr',{'itemtype':'http://schema.org/Article'})
    for topic in topics:
        parse_posts(topic.find('a',{'itemprop':'url'})['href'])

def parse_posts(url):
    
    totalpage = parse_totalpage(url)
    
    topic = None
    
    topicuuid = None
    topictitle = None
    
    try:
        for i in range(totalpage,0,-1):
            
            time.sleep(10)
            Session = sessionmaker()
            Session.configure(bind= engine)
            session = Session()
            
            postsurl = url+'page-'+str(i)
            postlists = []
            soup2 = BeautifulSoup(request.get(postsurl).content,'html.parser')
            
            if i == totalpage:#parse the title
                thirdpartyid=crackingpattern.match(url).group(1)
                existstopics =session.query(Topic).filter(Topic.third_party_id==thirdpartyid).filter(Topic.url==url).all()
                if existstopics:
                    topic = existstopics[0]
                    topicuuid = topic.uuid
                    topictitle = topic.name
                else:
                    topicuuid = str(uuid.uuid4())
                    topictitle = soup2.find('h1',{'class':'ipsType_pagetitle'}).getText().strip()
                    logging.info('---------------------------add topic------------------'+postsurl)
                    logging.info('topic title:\t'+topictitle)
                    logging.info('url:\t'+url)
                    logging.info('third party id:\t'+str(thirdpartyid))
                    createdate = soup2.find('span',{'itemprop':'dateCreated'}).getText().strip()
                    if 'Today,' in createdate:
                        createdate=createdate.replace('Today,',currentday)
                    elif 'Yesterday,' in createdate :
                        createdate=createdate.replace('Yesterday,',currentday)
                    createdate = datetime.strptime(createdate,'%b %d %Y %I:%M %p')
                    logging.info('created at:\t'+str(createdate))
                    topic = Topic(uuid=topicuuid,forum_uuid='17a51f9d-6e03-11e5-9db3-0cc47a34a45a',name=topictitle,url=url,created_at=createdate,third_party_id=thirdpartyid)
                    session.add(topic)
                    session.flush()
                    session.commit()
            posteles = soup2.findAll('div',id=re.compile('^post_id_\d+'))
            for postele in posteles:
                postid = postele['id'][8:]
                membername = postele.find('span',{'itemprop':'creator name'}).getText().strip()
                postnum = session.query(Post).filter(Post.third_party_id==postid).filter(Post.member_name==membername).count()
                
                if postnum >0:
                    logging.info('------------------exists post ----------\t'+postid)
                    break
                else:
                    posttime = datetime.strptime(postele.find('abbr',{'itemprop':'commentTime'})['title'], "%Y-%m-%dT%H:%M:%S+00:00")
                    postbody = postele.find('div',{'itemprop':'commentText'}).getText().strip()
                    logging.info("------------------create post ----------\t"+postid)
                    logging.info("post third party id:\t"+postid)
                    logging.info("post member name:\t"+membername)
                    logging.info("post body length:\t"+str(len(postbody)))
                    logging.info("post create time:\t"+str(posttime))
                    post = Post(uuid=str(uuid.uuid4()),thread_uuid=topicuuid,third_party_id=postid,member_name=membername,body=postbody,created_at=posttime)
                 
                if postnum == 0:
                    postlists.append(post)
             
            if postlists:
                session.bulk_save_objects(postlists)
                session.flush()
                session.commit()
                session.close()
            else:
                logging.info('++++++++++++++++++++++++++++no add posts,url:\t%s',postsurl)
        
    except exc.InvalidRequestError:
        logging.info('*********************add failed,the url is:\t%s',url)
        logging.info(traceback.format_exc())
    except requests.ConnectionError:
        logging.info('********************* connection failed,the url is:\t%s',url)
  
def dowork():
    while True:
        url = crackq.get()
        logging.info('++++++++++++++++++begin to processing url\t %s',url)
        parse_topics(url)
        crackq.task_done()
        time.sleep(2) 

if __name__=="__main__":
    starttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for i in range(crackconcurrent):
        t = Thread(target=dowork)
        t.daemon = True
        t.start()
        time.sleep(5)
    parse_module()
    endtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info('********start time:\t'+starttime)
    logging.info('********end time:\t'+endtime)