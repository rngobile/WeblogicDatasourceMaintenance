#!/bin/bash

if [ $# != 2 ]; then
    echo "Usage: ${0} <environment> <domain>"
    exit 1
fi

ENVIRONMENT=$1
DOMAIN=$2
BASE_DOMAIN=/u01/app/oracle/projects/aserver/domains
SCRIPT_PATH=/u01/scripts/projects/Weblogic_Datasource_Maintenance

echo --------------------- ${DOMAIN} ---------------------
echo
if [ -f ${BASE_DOMAIN}/${DOMAIN}/bin/setDomainEnv.sh ]; then
    . ${BASE_DOMAIN}/${DOMAIN}/bin/setDomainEnv.sh

    if [ -d ${SCRIPT_PATH} ]; then
        cd ${SCRIPT_PATH} 
        java weblogic.WLST DatasourceMaint.py ${ENVIRONMENT} ${DOMAIN}
    else
        echo "${0}: Error - Script path does not exists."
        exit 1
else
    echo "${0}: Error - Cannot set environment for ${BASE_DOMAIN}/${DOMAIN}"
    exit 1
fi
