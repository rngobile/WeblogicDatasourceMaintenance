#!/usr/bin/python
import sys,os,re
from weblogic.security.internal import *
from weblogic.security.internal.encryption import *

class Datasource:

    def __init__(self, dataSourceArray):
        self.name = dataSourceArray.getName()
        self.user = get("/JDBCSystemResources/"+ self.name +"/Resource/" + self.name + "/JDBCDriverParams/" + self.name + "/Properties/" + self.name + "/Properties/user/Value")

    def getUser(self):
        return self.user


"""
    def getStatus():
        #code

    def startup():
        #code

    def shutdown():
        #code

    def getUser():
        #code

    def getPassword():
        #code
"""