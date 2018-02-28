#!/usr/bin/python
from com.ziclix.python.sql import zxJDBC

class OracleDB:
    def __init__(self, dsURL, user, password, dsDriver):
        self.dsURL = dsURL
        self.user = user
        self.password = password
        self.dsDriver = dsDriver
        try:
            self.connection = zxJDBC.connect(self.dsURL, self.user, self.password, self.dsDriver)
        except Exception, e:
            return e

    
    def changePassword(self, newPassword):
        self.newPassword = newPassword
        self.cursor = self.connection.cursor()
        try:
            sql = 'alter user %s identified by "%s"' % (self.user, self.newPassword)
            self.cursor.execute(sql)
            #self.connection.commit()
        finally:
            self.connection.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()