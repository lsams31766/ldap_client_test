# update bmsmanagerid and manager for Enteprise prod - 2 records for Vlad
from ldap_client import *
from ldap3 import MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE, SUBTREE
import time
# Common variables
#  Enterprise directory
login_enterprise = 'enterprise_prod'
search_base_enterprise  = 'o=bms.com'
bms_ids = ['00583595','00520806']
manager_ids = ['00447026','00447026']
search_scope = SUBTREE
search_filter = []
modify_user_dn_enterprise = []
changes_manager = []
for i in range(len(bms_ids)):
    search_filter.append('(bmsid=' + bms_ids[i] + ')')
    modify_user_dn_enterprise.append('bmsid=' + bms_ids[i] + ',ou=People,o=bms.com')
    change_mgr = 'bmsid=' + manager_ids[i] + ',ou=People,o=bms.com'
    changes_manager.append({
        'bmsmanagersid': [(MODIFY_REPLACE, [manager_ids[i]])],
        'manager': [(MODIFY_REPLACE, [change_mgr])],
        })

for i in range(len(bms_ids)):
    print(f'Change manager for bmsid={bms_ids[i]}')
    _ = modify_ldap_user(login_enterprise, modify_user_dn_enterprise[i], changes_manager[i], None)
    # check it was changed
    _,results = ldap_search(login_enterprise, search_base_enterprise, search_filter[i], search_scope, 'bmsmanagersid')
    print(results)
    _,r = get_attr_value_if_exists(results, 'bmsmanagersid')
    print(f'User {bms_ids[i]} new bmsmanagerid {r}')
    _,results = ldap_search(login_enterprise, search_base_enterprise, search_filter[i], search_scope, 'manager')
    print(results)
    _,r = get_attr_value_if_exists(results, 'manager')
    print(f'User {bms_ids[i]} new manager {r}')
