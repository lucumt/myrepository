#-*- coding:utf-8 -*-
'''
Created on 2015-9-25

@author: Administrator
'''
import datetime
import requests
import re
import uuid
import logging
import time
import traceback

from bs4 import BeautifulSoup
from threading import Thread
from Queue import Queue
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

from models import Topic,Post

concurrent=6
q = Queue(concurrent*2)

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

request = requests.Session()
request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
request.mount('http://', adapter)
  
engine = create_engine('mysql://root:123456@127.0.0.1/alen?charset=utf8')  # 定义引擎 

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
        if itemid in['category_1']:
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
                    q.put(posturl)
            q.join()
            
    
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
                q.put(posturl)

def parse_topics(url):
    print '-------------------parsing page:\t',url
    soup2 = BeautifulSoup(request.get(url).content,'html.parser')
    topics = soup2.findAll('tr',{'itemtype':'http://schema.org/Article'})
    for topic in topics:
        parse_posts(topic.find('a',{'itemprop':'url'})['href'])

def parse_posts(url):
    
    totalpage = parse_totalpage(url)
    
    tid = str(uuid.uuid4()).replace('-', '')
    
    Session = sessionmaker()
    Session.configure(bind= engine)
    session = Session()
    
    addtopic = True
    addpost = True
    topic = None
    
    try:
        postlists = []
        for i in range(totalpage,0,-1):
            
            if not addpost:
                break
            
            postsurl = url+'page-'+str(i)
            soup2 = BeautifulSoup(request.get(postsurl).content,'html.parser')
            
            if i == totalpage:#parse the title
                topic = Topic(tid,soup2.find('h1',{'class':'ipsType_pagetitle'}).getText().strip(),url)
                topicnum =session.query(Topic).filter(Topic.name==topic.name).filter(Topic.url==url).count()
                if topicnum > 0:
                    addtopic = False
            posteles = soup2.findAll('div',id=re.compile('^post_id_\d+'))
            for postele in posteles:
                postid = postele['id']
                membername = postele.find('span',{'itemprop':'creator name'}).getText().strip()
                posttime = postele.find('abbr',{'itemprop':'commentTime'})['title']
                
                postnum = session.query(Post).filter(Post.postid==postid).filter(Post.posttime==posttime).filter(Post.membername==membername).count()
                if postnum >0:
                    addpost = False
                
                bodystr = None
                bodies = postele.find('div',{'class':'post_body'}).find('div',{'itemprop':'commentText'}).findAll('p',recursive=False)
                for body in bodies:
                    if bodystr == None:
                        bodystr = body.getText().strip()
                    else:
                        bodystr +='\n' + body.getText().strip()
                post = Post(postid,tid,posttime,membername,bodystr)
                
                if postnum == 0:
                    postlists.append(post)
        if topic:
            logging.info("Finished parse topic\t"+topic.name+'\t<=========>\t'+url+'\ttotal posts:\t'+str(len(postlists)))
            if addtopic:
                session.add(topic)
        else:
            print '++++++++++++++++++++++++++no add topic:\t',url
        
        if postlists:
            session.bulk_save_objects(postlists)
        else:
            print '++++++++++++++++++++++++++no add posts,url:\t',url
        
        if addtopic or postlists:
            session.flush()
            session.commit()
        session.close()
        
    except exc.InvalidRequestError:
        print '*********************add failed,the url is:\t',url
        print traceback.format_exc()
    except requests.ConnectionError:
        print '********************* connection failed,the url is:\t',url
  
def dowork():
    while True:
        url = q.get()
        parse_topics(url)
        print url
        q.task_done()
        time.sleep(2) 

if __name__=="__main__":
    starttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for i in range(concurrent):
        t = Thread(target=dowork)
        t.daemon = True
        t.start()
    parse_module()
    endtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print '********start time:\t',starttime
    print '********end time:\t',endtime

