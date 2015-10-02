#-*- coding:utf-8 -*-
'''
Created on 2015-9-26

@author: Administrator
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  Column,String,DateTime,Text

Base = declarative_base()

class Topic(Base):
    __tablename__ = 'topic'

    tid = Column('id',String(36),primary_key=True)
    name = Column('name',String(200))
    url = Column('url',String(200))

    def __init__(self,tid,name,url):
        self.tid = tid
        self.name = name
        self.url = url

    def __repr__(self):
        return "<Metadata('%s','%s','%s')>" % (self.tid,self.name,self.url)
    
class Post(Base):
    __tablename__='post'
    
    postid = Column('post_id',String(36),primary_key=True)
    topicid = Column('topic_id',String(36))
    posttime = Column('post_time',DateTime)
    membername = Column('member_name',String(100))
    body = Column('body',Text())
    
    def __init__(self,postid,topicid,posttime,membername,body):
        self.postid = postid
        self.topicid = topicid
        self.posttime = posttime
        self.membername = membername
        self.body = body
        
    def __repr__(self):
        return "<Metadata('%s','%s','%s','%s','%s')>" % (self.postid,self.topicid,self.posttime,self.membername,self.body)