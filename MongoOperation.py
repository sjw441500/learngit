#!/usr/bin/env python
# -*- coding:utf-8 -*-
import MongoConn,sys
sys.path.append('C:/Users/Administrator/Desktop')
class MongoOperation:
    #print('operation'+sys.getdefaultencoding())
    global dbconn
    global conn
    global users
    dbconn=MongoConn.MongoConn()
    dbconn.connect()
    conn=dbconn.getConn()
    users=conn.lifeba.users    
    def insert(self,listname): 
        users.insert(listname)
        
    
