'''
Created on Jul 14, 2023

@author: larry
'''

# hosts name, url,  ssl_or_not, DN and password
hosts_data = {
    'local1389':("ldap://localhost:1389",'cn=admin,dc=rahasak,dc=com','rahasak'),
    "dirtest-cl":('ldap://dirtest-cl.bms.com',
                  'cn=join engine,ou=nonpeople,o=bms.com',
                  'cpjevkstag'),
    "uno":('ldaps://usabrbmsdct001.uno.adt.bms.com:636',
          "CN=APP_JOINENGINE,OU=Service Accounts,OU=IMSS,DC=uno,DC=adt,DC=bms,DC=com",
          'CrasuT5Uzaq?XEt')
}
