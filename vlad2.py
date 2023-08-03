# update bmsmanagerid and manager for Enteprise prod - 4 records for Vlad
'''
bmsid       name        new manager         new manager bms id
00464460	Allen Mitts	Daniel P Amedro  	00139257
00593459	DAVID YEFROYEV	Daniel P Amedro  	00139257
00147280	Gene Farr	Daniel P Amedro  	00139257
00460453	Gordon Tsang	Daniel P Amedro  	00139257
'''

from ldap_client import *
from ldap3 import MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE, SUBTREE
import time
# Common variables
#  Enterprise directory
enterprise_creds = get_creds_from_server('enterprise')
search_base_enterprise  = 'o=bms.com'
bms_ids = ['00464460','00593459','00147280','00460453']
manager_ids = ['00139257','00139257','00139257','00139257']
search_scope = SUBTREE
search_filter = []
modify_user_dn_enterprise = []
changes_manager = []

# first save the 4 user's into ldif file
def save_to_ldif(filename):
    s = '(|'
    for id in bms_ids:
        s += '(bmsid=' + id + ')'
    s += ')'
    print('filter',s)
    search_filter_all_users = s
    _,results,ldif = ldap_search(enterprise_creds, search_base_enterprise, 
        search_filter_all_users, search_scope, '*',get_ldif=True)
    ldif_to_file(filename,ldif)

# now make the change

def make_changes():
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
        _ = modify_ldap_user(enterprise_creds, modify_user_dn_enterprise[i], changes_manager[i], None)
        # check it was changed
        _,results = ldap_search(enterprise_creds, search_base_enterprise, search_filter[i], search_scope, 'bmsmanagersid')
        print(results)
        _,r = get_attr_value_if_exists(results, 'bmsmanagersid')
        print(f'User {bms_ids[i]} new bmsmanagerid {r}')
        _,results = ldap_search(enterprise_creds, search_base_enterprise, search_filter[i], search_scope, 'manager')
        print(results)
        _,r = get_attr_value_if_exists(results, 'manager')
        print(f'User {bms_ids[i]} new manager {r}')

save_to_ldif('vlad_update_4_users_new.txt')
#make_changes()
