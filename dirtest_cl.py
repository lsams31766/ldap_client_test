'''
Created on Jul 14, 2023

@author: larry
'''
from ldap_client import *

# Needed for connect_ldap_server
DIR_SRVR = 'dirtest-cl'
server_url = hosts_data[DIR_SRVR][HD_URL]
auth_dn = hosts_data[DIR_SRVR][HD_DN]
auth_password = hosts_data[DIR_SRVR][HD_PW]

# Needed for get_ldap_users
search_base = 'o=bms.com'
# provide a uidNumber to search for. '*" to fetch all users/groups
#search_filter = '(uidNumber=500)'
#search_filter = '(cn=*)'
search_filter = '(bmsid=00105204)'
search_scope = SUBTREE
get_ldap_users(server_url, auth_dn, auth_password, search_base, search_filter, search_scope)
