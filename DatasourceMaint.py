#!/usr/bin/python
import sys,os,re
from weblogic.security.internal import *
from weblogic.security.internal.encryption import *
from NewGeneratePassword import *
from OracleDB import *

def getPassword(cService, dsname):
    passwordAES = ''
    passwordArrayEnc = get("/JDBCSystemResources/"+ dsname +"/Resource/" + dsname + "/JDBCDriverParams/" + dsname + "/PasswordEncrypted")
    for asciiCode in passwordArrayEnc:
        passwordAES += chr(asciiCode)
    return cService.decrypt(passwordAES)

# ToDo: Decouple this method into add and reset methods, Figure a better way to do this.
def configAdminServer(dsName, manage, targets, isTargeted=False):
    if "com.bea:Name=AdminServer,Type=Server" in str(targets):
        isTargeted = True
    
    try:
        if (manage == 'add') and not (isTargeted):
            edit()
            startEdit()
            cd("/JDBCSystemResources/" + dsName)
            cmo.addTarget(getMBean('/Servers/AdminServer'))
            save()
            activate()
        elif (manage == 'reset'):
            edit()
            startEdit()
            cd("/JDBCSystemResources/" + dsName)
            print "reset: " + str(targets)
            set('Targets',targets)
            save()
            activate()
        else:
            print "No Need"
    except Exception, e:
        cancelEdit('y')
        print e
        dumpStack()

# ToDo: rename this method
def getDatasourceState(dsName,command="testPool"):
    targets = get("/JDBCSystemResources/" + dsName + "/Targets")
    configAdminServer(dsName,'add',targets)
    print dsName + ":Are You Connected? " + str(get("/JDBCSystemResources/" + dsName + "/Targets"))
    serverRuntime()
    objArray = jarray.array([], java.lang.Object)
    strArray = jarray.array([], java.lang.String)
    if command == "testPool":
        try:
            cd('JDBCServiceRuntime/AdminServer/JDBCDataSourceRuntimeMBeans/' + dsName)
            checkDS = invoke('testPool',objArray,strArray)
            if (checkDS == None):
                status = "OK"
            else:
                status = "Failed - " + checkDS
        except Exception, e:
            status = 'Failed: ' + str(e)
    elif (command == "shutdown") or (command == "start"):
        try:
            cd('JDBCServiceRuntime/AdminServer/JDBCDataSourceRuntimeMBeans/' + dsName)
            checkDS = invoke(command,objArray,strArray)
        except Exception, e:
            print e
    else:
        print "Error: Available commands are testPool, start, shutdown."
    
    configAdminServer(dsName, 'reset', targets)
    serverConfig()
    return status

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

def printDatasourceInfo(dsName, dsUser, dsPassword, dsStatus, host, port, sid, stringArray, isSID):
    #update: make this into an array
    linebreak = '=' * 230
    prName = "|%s" % dsName.ljust(25)
    prUser = "|%s" % dsUser.center(30)
    prPassword = "|%s" % dsPassword.center(30)
    #prPassword = "|%s" % "<redacted>".center(30)
    prHost = "|%s" % host.center(30)
    prPort = "|%s" % port.center(6)
    prStatus = "|%s" % dsStatus.center(50)
    prSID = "|%s" % sid.center(20)
    prNewPassword = "|%s" % NewGeneratePassword().generate_pass().center(30)

    #print prName + prUser + prPassword + prHost + prPort + prSID + prNewPassword + prStatus + '|'
    stringArray.append(prName + prUser + prPassword + prHost + prPort + prSID + prNewPassword + prStatus + '|')
    stringArray.append(linebreak)
    return stringArray

def getDatasourceInfo(cService, passwordChangeList, getAllPasswords):
    linebreak = "=" * 230
    stringArray = []
    stringArray.append(linebreak)
    stringArray.append('|%s' % "Datasource".ljust(25) +
                        '|%s' % "Username".center(30) +
                        '|%s' % "Password".center(30) +
                        '|%s' % "Host".center(30) +
                        '|%s' % "Port".center(6) +
                        '|%s' % "SID/Service Name".center(20) +
                        '|%s' % "NewPassword".center(30) +
                        '|%s' % "Status".center(50)  + '|'
    )
    stringArray.append(linebreak)

    allJDBCResources = cmo.getJDBCSystemResources()
    for ds in allJDBCResources:
        dsName = ds.getName()
        print "="*20 + " " + dsName + " " + "="*20
        dsUser = get("/JDBCSystemResources/"+ dsName +"/Resource/" + dsName + "/JDBCDriverParams/" + dsName + "/Properties/" + dsName + "/Properties/user/Value")
        dsPassword = ''
        if (dsName in passwordChangeList) or getAllPasswords:
            dsPassword = getPassword(cService, dsName)
        dsStatus = getDatasourceState(dsName)
        dsURL = ds.getJDBCResource().getJDBCDriverParams().getUrl().lower()
        dsDriver = ds.getJDBCResource().getJDBCDriverParams().getDriverName().lower()
        if ("oracle" in dsURL) and ("oracle" in dsDriver):
            host, port, sid, isSID = getOracleDB(dsURL)
        #dsJNDI = dsResource.getJDBCDataSourceParams().getJNDINames()[0]

        stringArray = printDatasourceInfo(dsName, dsUser, dsPassword, dsStatus, host, port, sid, stringArray, isSID)
    for string in stringArray:
        print string

def main():
    environment = sys.argv[1]
    domain = sys.argv[2]
    hostUser = 'weblogic'
    hostPass = 'welcome1'
    domain_path = '/u01/fmw/soa/user_projects/domains/'
    passwordChangeList = ['rntest']
    getAllPasswords = False

    # you need to provide two parameters, environment and domain
    if environment == '' or domain == '' :
            print 'Please enter two parameters for environment and domain'

    path = domain_path + domain 
    security_path = path + "/security"

    # if the environment is QAM
    if environment == 'DEV' :

            hostIP = '172.x.x.x'

            if domain == 'SYNC':
                    hostPort = '8001'
            if domain == 'ASYNC':
                    hostPort = '8002'
            if domain == 'RSYNC':
                    hostPort = '8003'

    # If my environment is Production
    if environment == 'PROD' :

            hostIP = '192.168.254.134'

            if domain == 'compact_domain':
                    hostPort = '7001'
            if domain == 'soadomain':
                    hostPort = '7010'
            if domain == 'osbdomain':
                    hostPort = '8010'

    connect( hostUser , hostPass , 't3://' + hostIP + ':' + hostPort )

    if passwordChangeList or listPasswords:
        encryptionService = SerializedSystemIni.getEncryptionService(security_path)
        cService = ClearOrEncryptedService(encryptionService)

    allServers=domainRuntimeService.getServerRuntimes()

    getDatasourceInfo(allServers, cService, passwordChangeList, getAllPasswords)
        
    """
        db = OracleDB("192.168.254.134",1521,"soadb","rn_test",'\8f(F%hL?y6Hh[BaT]o2Fw\aZ',1)
        db.changePassword(password1.generate_pass())
    """
main()
