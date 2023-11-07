# simple ldapsearch code
import sys
from ldap_client import *
from ldap3 import MODIFY_REPLACE, SUBTREE

'''
dir_server = 'enterprise'
dir_creds = get_creds_from_server(dir_server)
search_base_enterprise  = 'o=bms.com'
'''
dir_server = 'dirtest-root'
#dir_server = 'enterprise'
dir_creds = get_creds_from_server(dir_server)
search_base_enterprise  = 'o=bms.com'


bms_id = '00146523'
search_filter = f'(bmsid={bms_id})'
search_scope = SUBTREE

_,results = ldap_search(dir_creds, search_base_enterprise, 
    search_filter, search_scope, ['dn','cn'])
print(results)

