#!/usr/bin/python
import sys,os,re
from weblogic.security.internal import *
from weblogic.security.internal.encryption import *
from NewGeneratePassword import *
#from OracleDB import *

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
            tempTargets = targets
            tempTargets.append(ObjectName('com.bea:Name=AdminServer,Type=Server'))
            newTargets = str(tempTargets).split('[')[1].split(']')[0]
            arrayTargets = newTargets.split(' ')
            targetLength = len(arrayTargets)

            if targetLength == 1:
                set('Targets', jarray.array([ObjectName(arrayTargets[0])],ObjectName))
            elif targetLength == 2:
                set('Targets', jarray.array([ObjectName(arrayTargets[0].rstrip(',')),ObjectName(arrayTargets[1])],ObjectName))
            elif targetLength == 3:
                set('Targets', jarray.array([ObjectName(arrayTargets[0].rstrip(',')),ObjectName(arrayTargets[1]).rstrip(','),ObjectName(arrayTargets[2])],ObjectName))
            elif targetLength == 4:
                set('Targets', jarray.array([ObjectName(arrayTargets[0].rstrip(',')),ObjectName(arrayTargets[1]).rstrip(','),ObjectName(arrayTargets[2]).rstrip(','),ObjectName(arrayTargets[3])],ObjectName))
            else:
                print dsName + ":Error - Target (" + str(arrayTargets) + ") Length is " + str(targetLength) + ": You're SOL."

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

# ToDo: rename this method
def getDatasourceState(dsName,command="testPool"):
    targets = get("/JDBCSystemResources/" + dsName + "/Targets")
    configAdminServer(dsName,'add',targets)
    print dsName + ":Are You Connected?" + str(get("/JDBCSystemResources/" + dsName + "/Targets"))
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
        except:
            status = 'Failed - Datasource not targeted to AdminServer'
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
    #print dsURL
    if len(dsURL.split('@')) == 2:
        dsn = dsURL.split('@')[1]
    else:
        dsn = dsURL.split(',',2)[2]
    
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

def getDatasourceInfo(cService):
    allJDBCResources = cmo.getJDBCSystemResources()
    for ds in allJDBCResources:
        dsName = ds.getName()
        dsUser = get("/JDBCSystemResources/"+ dsName +"/Resource/" + dsName + "/JDBCDriverParams/" + dsName + "/Properties/" + dsName + "/Properties/user/Value")
        dsPassword = getPassword(cService, dsName)
        dsStatus = getDatasourceState(dsName)
        dsURL = ds.getJDBCResource().getJDBCDriverParams().getUrl().lower()
        dsDriver = ds.getJDBCResource().getJDBCDriverParams().getDriverName().lower()
        if ("oracle" in dsURL) and ("oracle" in dsDriver):
            host, port, sid, isSID = getOracleDB(dsURL)
        #dsJNDI = dsResource.getJDBCDataSourceParams().getJNDINames()[0]

        printDatasourceInfo(dsName, dsUser, dsPassword, dsStatus, host, port, sid, isSID)

def printDatasourceInfo(dsName, dsUser, dsPassword, dsStatus, host, port, sid, isSID):
    #update: make this into an array
    linebreak = '=' * 200
    prName = "|%s" % dsName.ljust(20)
    prUser = "|%s" % dsUser.center(15)
    prPassword = "|%s" % dsPassword.center(30)
    prHost = "|%s" % host.center(20)
    prPort = "|%s" % port.center(6)
    prStatus = "|%s" % dsStatus.center(50)
    """
    print "Name:\t\t" + dsName
    print "User:\t\t" + dsUser
    print "Password:\t" + dsPassword
    print "Status:\t\t" + dsStatus
    print "\tHost:\t" + host
    print "\tPort:\t" + port
    """
    if isSID:
        prSID = "|%s" % sid.center(10)
        #print "\tSID:\t" + sid
    else:
        prSID = "|%s" % sid.center(10)
        #print "\tService Name:\t" + sid
    password1 = NewGeneratePassword()
    prNewPassword = "|%s" % password1.generate_pass().center(30)

    print prName + prUser + prPassword + prHost + prPort + prSID + prNewPassword + prStatus + '|'
    #print "\tNew Password:\t" + password1.generate_pass()
    print linebreak

def main():
    environment = sys.argv[1]
    domain = sys.argv[2]
    hostUser = 'weblogic'
    hostPass = 'welcome1'

    # you need to provide two parameters, environment and domain
    if environment == '' or domain == '' :
            print 'Please enter two parameters for environment and domain'

    path = "/u01/fmw/soa/user_projects/domains/" + domain + "/security"

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

    encryptionService = SerializedSystemIni.getEncryptionService(path)
    cService = ClearOrEncryptedService(encryptionService)

    getDatasourceInfo(cService)
        
    """
        db = OracleDB("192.168.254.134",1521,"soadb","rn_test",'\8f(F%hL?y6Hh[BaT]o2Fw\aZ',1)
        db.changePassword(password1.generate_pass())
    """
main()
