#!/usr/bin/python
import sys,os,re
from weblogic.security.internal import *
from weblogic.security.internal.encryption import *
import ConfigParser
import time as systime
from NewGeneratePassword import *
from OracleDB import *
from TableBuilder import *

def changeDSPassword(cService, dsName, newPassword):
    try:
        print "-- Changing weblogic " + dsName + " password --"
        edit()
        startEdit()
        encryptedPassword = cService.encrypt(newPassword)
        cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName)
        set('PasswordEncrypted',encryptedPassword)
        save()
        activate()
    except Exception, e:
        cancelEdit('y')
        print e

def getPassword(cService, dsname):
    passwordAES = ''
    passwordArrayEnc = get("/JDBCSystemResources/"+ dsname +"/Resource/" + dsname + "/JDBCDriverParams/" + dsname + "/PasswordEncrypted")
    for asciiCode in passwordArrayEnc:
        passwordAES += chr(asciiCode)
    return cService.decrypt(passwordAES)

def getDSResource(dsName):
    dsResources = domainRuntimeService.getDomainConfiguration().getJDBCSystemResources()
    if "Name="+dsName+"," in str(dsResources):
        for dsResource in dsResources:
            if dsName == dsResource.getName():
                return dsResource
    else:
        print "Error: No MBean Resource Found."

def manageDS(dsName, allServers, command="testPool"):
    status = []
    while True:
        try:
            domainRuntime()
        except:
            print "Retrying to Runtime.."
            systime.sleep(2)
            continue
        break
    for server in allServers:
        serverName = server.getName()
        jdbcRuntime = server.getJDBCServiceRuntime()
        datasources = jdbcRuntime.getJDBCDataSourceRuntimeMBeans()
        if "Name="+dsName+"," in str(datasources):
            while True:
                try:
                   cd('/ServerRuntimes/'+ serverName +'/JDBCServiceRuntime/' + serverName +'/JDBCDataSourceRuntimeMBeans/' + dsName)
                except:
                    print "Retrying to attach to Runtime Path.."
                    systime.sleep(2)
                    continue
                break
            
            while True:
                try:
                    state = cmo.getState()
                except:
                    print "Retrying to check State.."
                    systime.sleep(2)
                    continue
                break

            if command == "testPool":
                try:
                    if state in ("Shutdown","Suspended","Overloaded"):
                        status.append("[" + serverName + ":" + state + "]")
                    else:
                        test = cmo.testPool()
                        if test:
                            status.append("[" + serverName + ":" + str(test) + "]")
                        else:
                            status.append("[" + serverName + ":OK]")
                except Exception, e:
                    status.append("[" + serverName + ":" + str(e) + "]")
            elif command == "shutdown":
                if state != 'Shutdown':
                    print "-- Shutting down " + dsName + " on " + serverName + " --"
                    try:
                        cmo.shutdown()
                    except Exception, e:
                        print e
                    serverConfig()
                    return "offline"
                else:
                    serverConfig()
                    return state
            elif command == "start":
                print "-- Starting " + dsName + " on " + serverName + " --"
                try:
                    cmo.start()
                except Exception, e:
                    print e
                return state
            elif command == "reset":
                print "-- Resetting " + dsName + " on " + serverName + " --"
                try:
                    cmo.reset()
                except Exception, e:
                    print e
            elif command == "restartMBean":
                print "-- Restarting MBeans " + dsName + " on " + serverName + " --"
                dsResourceMBean = getDSResource(dsName)
                domainRuntimeService.getDomainRuntime().restartSystemResource(dsResourceMBean)
    serverConfig()
    return str(status)

def getOracleDB(dsURL):
    print "dsURL: " + str(dsURL)
    if len(dsURL.split('@')) == 2:
        dsn = dsURL.split('@')[1].lstrip('/')
    else:
        dsn = dsURL.split('/',2)[2]
    
    if len(dsn.split(':')) == 3:
        hostname = dsn.split(':')[0]
        sid = dsn.split(':')[2]
        port = dsn.split(':')[1]
        isSID = False
    elif len(dsn.split(':')) == 2:
        hostname = dsn.split(':')[0]
        sid = dsn.split('/')[1]
        port = dsn.split(':')[1].split('/')[0]
        isSID = True
    else:
        hostname = dsn.split('host=')[1].split(')')[0]
        port = dsn.split('port=')[1].split(')')[0]
        if 'service_name' in dsn:
            sid = dsn.split('service_name=')[1].split(')')[0]
            isSID = False
        else:
            sid = dsn.split('sid=')[1].split(')')[0]
            isSID = True
        
    return hostname, port, sid, isSID

def printDatasourceInfo(dataList):
    headerList = ['Datasource',
                  'Username',
                  'Password',
                  'Host',
                  'Port',
                  'SID/Service Name',
                  'New Password'
    ]

    monitorList = ['Datasource',
                   'Status'
    ]

    tb = TableBuilder(headerList, dataList)
    mon = TableBuilder(monitorList, dataList)

    columnLength = mon.buildTable(monitorList, dataList)
    mon.printTable(monitorList, dataList, columnLength)
    print "\n"
    columnLength = tb.buildTable(headerList, dataList)
    tb.printTable(headerList, dataList, columnLength)

def getDatasourceInfo(allServers, cService, passwordChangeList, dumpPasswords):
    host, port, sid, newPassword = "", "", "", ""
    isSID = True
    dataList = []

    allJDBCResources = cmo.getJDBCSystemResources()
    for ds in allJDBCResources:
        dsName = ds.getName()
        print "="*20 + " " + dsName + " " + "="*20
        dsUser = get("/JDBCSystemResources/"+ dsName +"/Resource/" + dsName + "/JDBCDriverParams/" + dsName + "/Properties/" + dsName + "/Properties/user/Value")
        dsPassword = ''
        dsURL = ds.getJDBCResource().getJDBCDriverParams().getUrl().lower().replace(' ','')
        dsDriver = ds.getJDBCResource().getJDBCDriverParams().getDriverName()
        #dsJNDI = dsResource.getJDBCDataSourceParams().getJNDINames()[0]

        if dumpPasswords in ['TRUE','T']:
            dsPassword = getPassword(cService, dsName)
            if ("oracle" in dsURL) and ("oracle" in dsDriver.lower()):
                host, port, sid, isSID = getOracleDB(dsURL)

        # Change Password if in passChangeList
        if dsName in passwordChangeList:
            if dumpPasswords not in ['TRUE','T']:
                dsPassword = getPassword(cService, dsName)
            state = manageDS(dsName, allServers, "shutdown")
            if ("oracle" in dsURL) and ("oracle" in dsDriver.lower()):
                host, port, sid, isSID = getOracleDB(dsURL)
                db = OracleDB(dsURL,dsUser,dsPassword,dsDriver)
                if hasattr(db, 'connection'):
                    newPassword = NewGeneratePassword().generate_pass()
                    db.changePassword(newPassword)
                    changeDSPassword(cService, dsName, newPassword)
                else:
                    newPassword = 'Error: DB error'
            if state == "offline":
                manageDS(dsName,allServers,"restartMBean")
                #manageDS(dsName,allServers,"start")
        dsStatus = manageDS(dsName, allServers)

        dataItem = { "Datasource": dsName,
                     "Username": dsUser,
                     "Password": dsPassword,
                     "Host": host,
                     "Port": port,
                     "SID/Service Name": sid,
                     "New Password": newPassword,
                     "Status": dsStatus
        }

        dataList.append(dataItem)
    return dataList

def main():
    environment = sys.argv[1]
    domain = sys.argv[2]
    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    # Get variables from config file
    realm = environment.upper() + '.' + domain.upper()
    host = config.get(realm, 'host')
    port = config.get(realm, 'port')
    user = config.get(realm, 'user')
    password = config.get(realm, 'password')
    userKeyPath = config.get(realm, 'userKeyPath')
    configFilePath = config.get(realm, 'configFilePath')
    domainPath = config.get(realm, 'domainPath')
    passwordChangeList = config.get(realm, 'passwordChangeList').split(',') 
    dumpPasswords = config.get(realm, 'dumpPasswords').upper()
    t3url = 't3://' + host + ':' + port
    path = domainPath + domain 

    if userKeyPath and configFilePath:
        connect(userConfigFile=configFile, userKeyFile=userKey, url=t3url)
    elif user and password:
        connect( user , password , t3url)
    else:
        sys.exit("Error: Please assign correct credentials in config file.")

    if passwordChangeList or (dumpPasswords in ['TRUE','T']):
        encryptionService = SerializedSystemIni.getEncryptionService(path)
        cService = ClearOrEncryptedService(encryptionService)

    allServers=domainRuntimeService.getServerRuntimes()

    dataList = getDatasourceInfo(allServers, cService, passwordChangeList, dumpPasswords)
    printDatasourceInfo(dataList)
        
if __name__ == 'main':
    main()
