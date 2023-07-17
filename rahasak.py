from ldap_client import *
import json

# Needed for connect_ldap_server
login = hosts_data['local1389']

search_base = 'dc=rahasak,dc=com'
search_filter = '(sn=7)'
search_scope = SUBTREE
attrs = ['*'] 
success,results = ldap_search(*login, search_base, search_filter, search_scope, attrs)
if success:
    print(json.dumps(results,indent=4))