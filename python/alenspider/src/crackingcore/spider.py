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

from bs4 import BeautifulSoup
from models import Thread,Post

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

request = requests.Session()
request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'

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
    eles = soup.find('div',id='category_1').findAll('h4',{'class':'forum_name'})
    for ele in eles:
        url = ele.strong.a['href']
        print url
        
        #parse topic for submodule
        parse_subforum_topic(url)
        
        #get the total page of each subitem
        totalpage = parse_totalpage(url)
        
        #parse topic in each page       
        for i in range(1,totalpage+1):
            posturl = url+'page-'+str(i)+'?prune_day=100&sort_by=Z-A&sort_key=last_post&topicfilter=all'
            parse_topics(posturl)
    
#     parse_information('http://www.crackingcore.com/topic/77557-trusted-seller-section/')
def parse_subforum_topic(url):
    soup = BeautifulSoup(request.get(url).content,'html.parser')
    links = soup.findAll('div',{'class':'f_name'})
    if links:
        logging.info("**************begin to parse submodule for*************")
        for link in links:
            url = link.find('a')['href'].strip()
            totalpage = parse_totalpage(url)
            for i in range(1,totalpage+1):
                posturl = url+'page-'+str(i)+'?prune_day=100&sort_by=Z-A&sort_key=last_post&topicfilter=all'
                parse_topics(posturl)

def parse_topics(url):
    soup2 = BeautifulSoup(request.get(url).content,'html.parser')
    threads = soup2.findAll('tr',{'itemtype':'http://schema.org/Article'})
    for thread in threads:
        parse_posts(thread.find('a',{'itemprop':'url'})['href'])

threads = []
posts = []
def parse_posts(url):
    
    totalpage = parse_totalpage(url)
    
    for i in range(1,totalpage+1):
        
        postsurl = url+'page-'+str(i)
        soup2 = BeautifulSoup(request.get(postsurl).content,'html.parser')
        
        threadid = str(uuid.uuid4()).replace('-', '')
        
        if i == 1:#parse the title
            theme = Thread(threadid,soup2.find('h1',{'class':'ipsType_pagetitle'}).getText().strip(),url)
            threads.append(theme)
            logging.info("parsing thread:\t"+theme.name+'\t<=========>\t'+url)
        posteles = soup2.findAll('div',id=re.compile('^post_id_\d+'))
        for postele in posteles:
            postid = postele['id']
            membername = postele.find('span',{'itemprop':'creator name'}).getText().strip()
            posttime = postele.find('abbr',{'itemprop':'commentTime'})['title']
            bodystr = None
            bodies = postele.find('div',{'class':'post_body'}).find('div',{'itemprop':'commentText'}).findAll('p',recursive=False)
            for body in bodies:
                if bodystr == None:
                    bodystr = body.getText().strip()
                else:
                    bodystr +='\n' + body.getText().strip()
            post = Post(postid,threadid,posttime,membername,bodystr)
            posts.append(post)        
    

if __name__=="__main__":
    starttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parse_module()
#     soup = BeautifulSoup(request.get('http://www.crackingcore.com/forum/4-staff-information-applications/page-1?prune_day=100&sort_by=Z-A&sort_key=last_post&topicfilter=all').content,'html.parser')
#     parse_subforum_topic(soup)
    print 'threads number:\t',len(threads)
    print 'posts number:\t',len(posts)
    endtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print '********start time:\t',starttime
    print '********end time:\t',endtime

