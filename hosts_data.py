'''
Created on Jul 14, 2023

@author: larry
'''

# hosts name, url,  ssl_or_not, DN and password
HD_URL = 0
HD_SSL = 1
HD_DN = 2
HD_PW = 3
hosts_data = {
    "local1389":("ldap://localhost:1389",False,'cn=admin,dc=rahasak,dc=com','rahasak'),
}
# access like: hosts_data['local1389'][HD_URL]
