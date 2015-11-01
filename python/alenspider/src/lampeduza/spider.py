#-*-coding:utf-8-*-
'''
Created on 2015-10-25

@author: Administrator
'''
import logging
import requests
import re


from bs4 import BeautifulSoup
from datetime import datetime

request = requests.Session()
request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=1000)
request.mount('http://', adapter)

logfilename = 'lampeduza_'+datetime.now().strftime("%Y_%m_%d")+'.log'
logging.basicConfig(name='inlampeduza',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

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
#     if url != 'https://lampeduza.so/forum/14-иски-суд-список-брутов/':
#         return
    response = request.get(url).content
    soup = BeautifulSoup(response,'lxml')
    totalpage = parse_total_page(soup)
    for i in range(totalpage):
        topicurl=url+'page-'+str(i+1)+'?prune_day=100&sort_by=Z-A&sort_key=last_post&topicfilter=all'
        logging.info('----------------Begin to parse url------------:\t'+topicurl)
        if i>0:
            response = request.get(topicurl).content
            soup=BeautifulSoup(response,'lxml')
        parse_topic(soup)

def parse_topic(soup):
    tds = soup.findAll('td',{'class':'col_f_content'})
    for td in tds:
        logging.info('---------------------------------------')
        link = td.h4.a
        linkinfos=link['title'].split('- started')
        
        url = link['href']
        logging.info('third party id:\t'+link['id'].strip()[9:])
        logging.info('name:\t'+linkinfos[0].strip())
        logging.info('url:\t'+url)
        if linkinfos[1].strip() !='--':
            logging.info('created_at:\t'+str(datetime.strptime(linkinfos[1].strip(),'%d %B %Y - %I:%M %p')))
        parse_posts(url)
            
def parse_posts(url):
    response=requests.get(url).content
    soup = BeautifulSoup(response)
    totalpage=parse_total_page(soup)
    for i in range(totalpage):
        posturl=url+'page-'+str(i+1)
        if i>0:
            response=requests.get(posturl).content
            soup = BeautifulSoup(response)
        posts=soup.findAll('div',{'class':'post_block'})
        for post in posts:
            pname = post.find('div',{'class':'post_username'}).getText().strip()
            pdate = post.find('div',{'class':'post_date'}).abbr['title']
            pdate = datetime.strptime(pdate,'%Y-%m-%dT%H:%M:%S+00:00')
            logging.info('---------------------------------------')
            logging.info('Third party id:\t'+post['id'][8:])
            logging.info('Member name:\t'+pname)
            logging.info('Created date:\t'+str(pdate))
            logging.info('Post body length:\t'+str(len(post.find('div',{'class':'post_body'}).div.getText().strip())))

if __name__ == '__main__':
    starttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parse_lampeduza()
    endtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print 'start time',starttime
    print 'end time',endtime