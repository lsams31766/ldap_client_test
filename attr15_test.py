#attr15_test.py
'''
  Test setting of attributeExtesion15


PRE-TEST
  change JE rule for Azure extension15 - bmsid=95450027 - ALLOW FOR THIS ID ONLY!!!

Test Commands: 
   PRETEST
1) CHECK: extensionAttribute15 is present and TRUE in UNO for bmsid=95450027
2) disable account in dirtest: 
  DN: bmsid=95450027,ou=People,o=bms.com
  BMSEntAccountStatus: Disabled
3) CHECK:  extensionAttribute15 is GONE in UNO - may take 15 minutes

   CHANGE BEHAVIOUR AND SETUP
4) CHANGE JOIN ENGINE RULE: Constructed Attributes, AzureADFlag, Default: FILTER bmsid=1
5) enable account in dirtest
6) Bring back extension15, set to TRUE in UNO for bmsid=95450027
7) CHECK: extensionAttribute15 is present and TRUE 
  
    TEST NEW FUNCTIONALITY
8) disable account in dirtest:
  DN: bmsid=95450027,ou=People,o=bms.com
  BMSEntAccountStatus: Disabled
9) CHECK: extensionAttribute15 is STILL PRESENT and TRUE - check 15 minutes later to verify it sticks
   
   POST Test - Restore to normal
10) enable account in dirtest
  DN: bmsid=95450027,ou=People,o=bms.com
  BMSEntAccountStatus: Disabled
11) restore extension15 in UNO
12) CHECK: extensionAttribute15 is present and TRUE in UNO 
'''
from ldap_client import *
from ldap3 import MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE, SUBTREE
# Common variables
#  UNO
login_uno = 'uno'
search_base_uno = 'DC=uno,DC=adt,DC=bms,DC=com'
search_filter = '(bmsid=95450027)'
search_scope = SUBTREE
attrs_ea15 = ['extensionAttribute15'] 
modify_user_dn_uno = "CN=Baldassarre\, Adriana (95450027),OU=BMS Users,DC=uno,DC=adt,DC=bms,DC=com"
  # Add ext15
changes_add_ext15 = {
    'extensionAttribute15': [(MODIFY_ADD, ['TRUE'])]
    }
  # Delete ext15
changes_delete_ext15 = {
    'extensionAttribute15': [(MODIFY_DELETE, [])]
    }
#  dirtest
login_dirtest = 'dirtest_cl'
modify_user_dn_dirtest = "bmsid=95450027,ou=People,o=bms.com"
changes_disabled = {
    'BMSEntAccountStatus': [(MODIFY_REPLACE, ['Disabled'])]
    }
changes_enabled = {
    'BMSEntAccountStatus': [(MODIFY_REPLACE, ['Enabled'])]
    }
search_ea15 = 'OU=BMS Users,DC=uno,DC=adt,DC=bms,DC=com'
filter_ea15 = '(bmsid=95450027)'

# TEST if extensionAttribute15 exists?
'''
_,results = ldap_search(login_uno, search_ea15, filter_ea15, search_scope, 'extensionAttribute15')
_,r = get_attr_value_if_exists(results, 'extensionAttribute15')
print(f'does extensionAttribute15 exist? results {r}') 
if r:
    # now delete it
    print('DELETE extensionAttribute15')
    _ = modify_ldap_user(login_uno, modify_user_dn_uno, changes_delete_ext15, None)
    _,results = ldap_search(login_uno, search_ea15, filter_ea15, search_scope, 'extensionAttribute15')
    _,r = get_attr_value_if_exists(results, 'extensionAttribute15')
    print(f'does extensionAttribute15 exist? results {r}') 
# now add it back
print('ADD extensionAttribute15')
_ = modify_ldap_user(login_uno, modify_user_dn_uno, changes_add_ext15, None)
_,results = ldap_search(login_uno, search_ea15, filter_ea15, search_scope, 'extensionAttribute15')
_,r = get_attr_value_if_exists(results, 'extensionAttribute15')
print(f'does extensionAttribute15 exist? results {r}') 
exit(0)
'''

# Pretest 1 - extensionAttribute15 is present and TRUE in UNO for bmsid=95450027
s,results = ldap_search(login_uno, search_base_uno, search_filter, search_scope, attrs_ea15)
_,results = ldap_search(login_uno, search_ea15, filter_ea15, search_scope, 'extensionAttribute15')
_,r = get_attr_value_if_exists(results, 'extensionAttribute15')
if not r:
    print('Pretest 1 - did not find extensionAttribute15')
    exit(1)
s = check_attrib_matched(results, 'extensionAttribute15', 'TRUE')
if not s:
    print('Pretest 1 - extensionAttribute15 - wrong value!')
    exit(1)
# Pretest 2 - disable account in dirtest
print('Disable account')
_ = modify_ldap_user(login_dirtest, modify_user_dn_dirtest, changes_enabled, None)
# Pretest 3 - CHECK:  extensionAttribute15 is GONE in UNO
# MAY HAVE TO LOOP THIS!
s,results = ldap_search(login_uno, search_base_uno, search_filter, search_scope, attrs_ea15)
_,r = get_attr_value_if_exists(results, 'extensionAttribute15')
if r:
    print('Pretest 1- Still have extensionAttribute15 in UNO')
    exit(1)
exit(0)
#------------------------------------------------------------------------------
# CHANGE BEHAVIOUR AND SETUP
# 4) CHANGE JOIN ENGINE RULE: Constructed Attributes, AzureADFlag, Default: FILTER bmsid=1
# 5) enable account in dirtest
s = modify_ldap_user(login_dirtest, modify_user_dn, changes_enabled, None)
# 6) Bring back extension15, set to TRUE in UNO for bmsid=95450027
s = modify_ldap_user(login_uo, modify_user_uno_dn, changes_add_ext15, None)
# 7) CHECK: extensionAttribute15 is present and TRUE
s,results = ldap_search(login_uno, search_base_uno, search_filter, search_scope, attrs_ea15)
#--------------------------------------------------------------------------------
