#!/usrbin/env python
# -*- coding:utf-8 -*-

import pymongo,traceback,sys

class MongoConn:
    conn=None
    #print('conn'+sys.getdefaultencoding())
    servers='mongodb://localhost:27017'
    def connect(self):
        try:
            self.conn=pymongo.Connection(self.servers)
            print('success to connect')
        except Exception:
            print('fault')
    def close(self):
        return self.conn.disconnect()
    def getConn(self):
        return self.conn
        
