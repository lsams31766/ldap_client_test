'''
Created on Jul 14, 2023

@author: larry
'''
from ldap_client import *

# Needed for connect_ldap_server
login = hosts_data['dirtest-cl']

# Needed for get_ldap_users
search_base = 'o=bms.com'
# provide a uidNumber to search for. '*" to fetch all users/groups
#search_filter = '(uidNumber=500)'
#search_filter = '(cn=*)'
search_filter = '(bmsid=00105204)'
search_scope = SUBTREE
attrs = ['cn','sn','uid','bmsentaccountstatus','extensionAttribute15'] 
success,results = ldap_search(*login, search_base, search_filter, search_scope, attrs)
if success:
    for r in results:
        print(r)