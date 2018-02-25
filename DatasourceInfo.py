#miguel.ortiz
import sys,os,re
from weblogic.security.internal import *
from weblogic.security.internal.encryption import *

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
        if domain == 'ASYNC':
                hostPort = '8002'
        if domain == 'RSYNC':
                hostPort = '8003'
dsCounter = 0


# Connect to the host
connect( hostUser , hostPass , 't3://' + hostIP + ':' + hostPort )

encryptionService = SerializedSystemIni.getEncryptionService(path)
cService = ClearOrEncryptedService(encryptionService)

# get all JDBC Properties
allJDBCResources = cmo.getJDBCSystemResources()
for jdbcResource in allJDBCResources:
        dsCounter +=1
        dsname = jdbcResource.getName()
        dsResource = jdbcResource.getJDBCResource()
        dsJNDIname = dsResource.getJDBCDataSourceParams().getJNDINames()#[0]
        dsInitialCap = dsResource.getJDBCConnectionPoolParams().getInitialCapacity()
        dsMaxCap = dsResource.getJDBCConnectionPoolParams().getMaxCapacity()
        dsParams = dsResource.getJDBCDataSourceParams()
        dsDriver = dsResource.getJDBCDriverParams().getDriverName()
        conn =  dsResource.getJDBCDriverParams().getUrl()
        test = dsResource.getJDBCDriverParams().getProperties()
        test1 = dsResource.getJDBCConnectionPoolParams()
        user = ''
        readTimeOut = ''
        conTimeOut = ''
        streamAsBlob = ''
	target = ''
	password = ''
	passwordAES = ''
	passwordEncList = []
       
        redirect('file','false')	
	try :
	 	user = get("/JDBCSystemResources/"+ dsname +"/Resource/" + dsname + "/JDBCDriverParams/" + dsname + "/Properties/" + dsname + "/Properties/user/Value")
	 	passwordEncList =  get("/JDBCSystemResources/"+ dsname +"/Resource/" + dsname + "/JDBCDriverParams/" + dsname + "/PasswordEncrypted")
		for asciiCode in passwordEncList:
			passwordAES += chr(asciiCode)
		password = cService.decrypt(passwordAES)
	 	readTimeOut = get("/JDBCSystemResources/"+ dsname +"/Resource/" + dsname + "/JDBCDriverParams/" + dsname + "/Properties/" + dsname + "/Properties/oracle.jdbc.ReadTimeout/Value")
	 	conTimeOut = get("/JDBCSystemResources/"+ dsname +"/Resource/" + dsname + "/JDBCDriverParams/" + dsname + "/Properties/" + dsname + "/Properties/oracle.net.CONNECT_TIMEOUT/Value")
	 	streamAsBlob = get("/JDBCSystemResources/"+ dsname +"/Resource/" + dsname + "/JDBCDriverParams/" + dsname + "/Properties/" + dsname + "/Properties/SendStreamAsBlob/Value")
	except WLSTException:
		# omitimos errores por la no existencia de las propiedades buscadas con ls()
		pass
	stopRedirect()	

	print 'datasource.name.' + str(dsCounter) +'=' + str(dsname)
	print 'datasource.jndiname.' + str(dsCounter) + '=' + str(dsJNDIname)
	print 'datasource.driver.class.' + str(dsCounter) + '=' + dsDriver
	print 'datasource.url.' + str(dsCounter) + '=' + conn
	print 'datasource.readTimeout.' + str(dsCounter) + '=' + readTimeOut 
	print 'datasource.connectionTimeout.' + str(dsCounter) + '=' + conTimeOut 
	print 'datasource.username.' + str(dsCounter) + '=' + user
	print 'datasource.password.' + str(dsCounter) + '=' + password
	print 'datasource.initialCapacity.' + str(dsCounter) + '=' + str(dsInitialCap)
	print 'datasource.maxCapacity.' + str(dsCounter) + '=' + str(dsMaxCap)
	print 'datasource.target.' + str(dsCounter) + '=' + target
	if not streamAsBlob :
		getStreamAsBlob = 'false'
	else :
		print '#datasource.sendStreamAsBlob.' + str(dsCounter) + '=' + streamAsBlob

	print '\n'
