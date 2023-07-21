'''
Created on Jul 14, 2023

@author: larry
'''

# hosts name, url,  ssl_or_not, DN and password
hosts_data = {
    'local1389':("ldap://localhost:1389",'cn=admin,dc=rahasak,dc=com'),
    "dirtest_cl":('ldap://dirtest-cl.bms.com',
                  'cn=join engine,ou=nonpeople,o=bms.com'),
    "uno":('ldaps://usabrbmsdct001.uno.adt.bms.com:636',
          "CN=APP_JOINENGINE,OU=Service Accounts,OU=IMSS,DC=uno,DC=adt,DC=bms,DC=com"),
    "metaview_uat":('ldap://metaview-uat.bms.com:389',
                  'cn=join engine,ou=nonpeople,o=bms.com'),
    "enterprise_prod":('ldap://directory-cl.bms.com',
                  'cn=join engine,ou=nonpeople,o=bms.com'),
    "metaview_prod":('ldap://metaview.bms.com:389',
                  'cn=join engine,ou=nonpeople,o=bms.com'),
    "ad_prod":('ldaps://adjoin-na.one.ads.bms.com:636',
                  'CN=APP_JOINENGINE,OU=Service Accounts,OU=IMSS,DC=one,DC=ads,DC=bms,DC=com'),
    "metasupplier_prod":('ldap://uslvlbmsasp175.net.bms.com:389',
                  'cn=join engine,ou=nonpeople,o=bms.com'),
}
