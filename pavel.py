# update bmsa in direst prod for bmsid's given
from ldap_client import *
from ldap3 import MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE, SUBTREE
import time
# Common variables
#  Enterprise directory
login_enterprise = 'enterprise_prod'
search_base_enterprise  = 'o=bms.com'
search_filter = '(bmsid=00602724)'
search_scope = SUBTREE
modify_user_dn_dirtest = "bmsid=00602724,ou=People,o=bms.com"
changes_bms_a = {
    'bmsa': [(MODIFY_REPLACE, ['x'])]
    }

login_metaview = 'metaview_prod'
search_base_metaview  = 'o=bms.com'
login_ad = 'ad_prod'
search_base_ad  = 'DC=one,DC=ads,DC=bms,DC=com'
login_metasupplier = 'metasupplier_prod'
search_base_metasupplier  = 'o=bms.com'



# _ = modify_ldap_user(login_dirtest, modify_user_dn_dirtest, changes_bms_a, None)
# check it was changed
_,results = ldap_search(login_enterprise, search_base_enterprise, search_filter, search_scope, 'bmsa')
print(results)
_,r = get_attr_value_if_exists(results, 'bmsa')
print(f'change bmsa got {r}')
# check bmsentaccountstatus in diretest
print('check dirtest for bmsentaccountstatus')
_,results = ldap_search(login_enterprise, search_base_enterprise, search_filter, search_scope, 'bmsentaccountstatus')
print(results)
_,r = get_attr_value_if_exists(results, 'bmsentaccountstatus')
print(f'change bmsentaccountstatus got {r}')


# check metaview
print('Check metaview...')
_,results = ldap_search(login_metaview, search_base_metaview, search_filter, search_scope, 'bmsentaccountstatus')
print(results)
_,r = get_attr_value_if_exists(results, 'bmsentaccountstatus')
print(f'METAVIEW bmsentaccountstatus got {r}')

# check active directory
print('Check AD...')
_,results = ldap_search(login_ad, search_base_ad, search_filter, search_scope, 'bmsentaccountstatus')
print(results)
_,r = get_attr_value_if_exists(results, 'bmsentaccountstatus')
print(f'AD bmsentaccountstatus got {r}')

# check metasupplier
print('Check METASUPPLIER...')
_,results = ldap_search(login_metasupplier, search_base_metasupplier, search_filter, search_scope, 'bmsentaccountstatus')
print(results)
_,r = get_attr_value_if_exists(results, 'bmsentaccountstatus')
print(f'METASUPPLIER bmsentaccountstatus got {r}')
