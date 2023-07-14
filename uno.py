'''
Created on Jul 14, 2023

@author: larry
'''
from ldap_client import *

# Needed for connect_ldap_server
login = hosts_data['uno']

# Needed for get_ldap_users
search_base = 'DC=uno,DC=adt,DC=bms,DC=com'
# provide a uidNumber to search for. '*" to fetch all users/groups
#search_filter = '(uidNumber=500)'
#search_filter = '(cn=*)'
search_filter = '(bmsid=95450027)'
search_scope = SUBTREE
get_ldap_users(*login, search_base, search_filter, search_scope)
