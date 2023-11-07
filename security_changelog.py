#security_change_log.py
import sys
from ldap_client import *
from ldap3 import SUBTREE,DEREF_ALWAYS,LEVEL
import json
from collections import defaultdict

dir_server = 'lvlrootdir'
dir_creds = get_creds_from_server(dir_server)
search_base = 'cn=changelog'
search_filter = '(objectClass=*)'
search_scope = SUBTREE
_,results= paged_search(dir_creds, search_base, 
           search_filter, search_scope, "+")
print(f'found {len(results)} records')
print(results)
