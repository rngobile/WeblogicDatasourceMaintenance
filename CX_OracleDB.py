#!/usr/bin/python
import cx_Oracle

class CX_OracleDB:

    def __init__(self, host, port, sid, user, password, isSID):
        self.host = host
        self.port = port
        self.sid = sid
        self.user = user
        self.password = password
        self.isSID = isSID

        if self.isSID:
            self.dsn = cx_Oracle.makedsn(self.host, self.port, self.sid)
        else:
            self.dsn = cs_Oracle.makedsn(self.host, self.port, service_name=self.sid)
        
        self.connection = cx_Oracle.connect(self.user, self.password, self.dsn)
    
    def buildStatement(self):
        #self.sqltext = 'alter user rn_test identified by rn_test'
        self.sqltext = 'select :usr, ":newpwd" from dual'
        return self.sqltext
    
    def executeStatement(self, newPassword):
        self.newPassword = newPassword
        self.sql = self.buildStatement()
        
        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute(self.sql, {"usr" : str(self.user),
                                            "newpwd" : str(self.newPassword)})
            result = self.cursor.fetchall()
            print result
        except cx_Oracle.DatabaseError, e:
            print e
    
    def changePassword(self, newPassword):
        self.newPassword = newPassword
        try:
            self.connection.changepassword(self.password,self.newPassword)
        except cx_Oracle.DatabaseError, e:
            print e 
        
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
