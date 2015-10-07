#-*- coding:utf-8 -*-
'''
Created on 2015-9-26

@author: Administrator
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  Column,String,DateTime,Text,Integer,CHAR,VARCHAR

Base = declarative_base()

class Topic(Base):
    __tablename__ = 'threads'

    tid = Column('id',Integer,primary_key=True)
    uuid = Column('uuid',CHAR(36),unique=True)
    forum_uuid = Column('forum_uuid',CHAR(36),default='')
    third_party_id = Column('third_party_id',VARCHAR(64),default='')
    name = Column('name',VARCHAR(255),default='')
    created_at = Column('created_at',DateTime)
    url = Column('url',VARCHAR(255),default='')

    def __init__(self,uuid,forum_uuid,third_party_id,name,created_at,url):
        self.uuid = uuid
        self.forum_uuid= forum_uuid
        self.third_party_id = third_party_id
        self.name = name
        self.created_at = created_at
        self.url = url

    def __repr__(self):
        return "<Metadata('%s','%s','%s','%s','%s','%s','%s')>" % (self.tid,self.uuid,self.forum_uuid,self.third_party_id,self.name,self.created_at,self.url)
    
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