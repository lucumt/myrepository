#-*- coding:utf-8 -*-
'''
Created on 2015-9-26

@author: Administrator
'''

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