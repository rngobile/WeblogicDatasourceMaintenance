# Weblogic Datasource Maintenance

This project was created to maintain Weblogic datasource passwords. The procedure will generate a random password of length 25, shutdown the datasource, update password of the user on the database, update Weblogic datasource password, reset the datasource, then test the datasource.

## Setting up the config.ini

The project will scan the config file to match the Environment followed by Domain:

**[PROD.COMPACT_DOMAIN]**  
**host**=*The admin DNS or IP for the domain*  
**port**=*The admin port for the domain*  
**user**=*If no keypair is set up to login for WLST, this is the clear text username*   
**password**=*If no keypair is set up to login for WLST, this is the clear text password*  
**userKeyPath**=*This is the path to the key file for login*  
**configFilePath**=*This is the path to the config file for login*  
**domainPath**=*This is the path to the base domain directory*  
**passwordChangeList**=*List of datasources to change passwords, seperated by commas*  
**dumpPasswords**=*boolean value to dump passwords, accepted choices are True, T, False, F*

example config.ini:
```
[PROD.COMPACT_DOMAIN]
host=localhost
port=7001
user=weblogic
password=welcome1
userKeyPath=
configFilePath=
domainPath=/u01/fmw/soa/user_projects/domains/
passwordChangeList=rntest
dumpPasswords=False

[PROD.COMPACT_DOMAIN]
host=localhost
port=7001
user=
password=
userKeyPath=/u01/fmw/keystore/mykey.secure
configFilePath=/u01/fmw/keystore/myconfigfile.secure
domainPath=/u01/fmw/soa/user_projects/domains/
passwordChangeList=myDatasource1,myDatasource2,myDatasource3
dumpPasswords=False
```

## Setting up monthly password changes

The `DatasourceMaintenance.sh` script is used to set environment and invoke the WLST python scripts. When this added to the user's crontab, we can automate the password change on a schedule.

Usage:
```
DatasourceMaintenance.sh <ENVIRONMENT> <DOMAIN>
```

You should configure the following variables inside the script:
**BASE_DOMAIN**=*This is the path to the base domain directory*  
**SCRIPT_PATH**=*The path where DatasourceMaint.py is located*  

Make the script executable to the user:
```
chmod +x DatasourceMaintenance.sh
```

Example:
```
BASE_DOMAIN=/u01/app/oracle/projects/aserver/domains
SCRIPT_PATH=/u01/scripts/projects/Weblogic_Datasource_Maintenance
```

## Crontab entry:

Modify the crontab to schedule your monthly password change:

crontab time format:
```
* * * * * *
| | | | | | 
| | | | | +-- Year              (range: 1900-3000)
| | | | +---- Day of the Week   (range: 1-7, 1 standing for Monday)
| | | +------ Month of the Year (range: 1-12)
| | +-------- Day of the Month  (range: 1-31)
| +---------- Hour              (range: 0-23)
+------------ Minute            (range: 0-59)
```

Example below for 12:00AM at the first of every month. A sepearte entry for each Domain will be needed:
```
00 00 1 * * /u01/scripts/DatasourceMaintenance.sh PROD compact_domain 2>&1 | tee /u01/logs/datasource_maint_prod_compact_domain.log
```
