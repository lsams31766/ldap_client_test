from ldap_client import *
from ldap3 import MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE, SUBTREE
import time

enterprise_creds = get_creds_from_server('enterprise')
search_base_enterprise  = 'o=bms.com'
search_filter = '(mail=Ger.Power@bms.com)'
search_scope = SUBTREE
s,r = ldap_search(enterprise_creds, search_base_enterprise, search_filter, 
    search_scope, ['bmsid','mail'])
print(r)

