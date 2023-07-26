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
import time
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
search_dirtest_base = 'o=bms.com'
search_ditest_filter = '(bmsid=95450027)'
attr_bmsEntAccountStatus = 'BMSEntAccountStatus'
search_ea15 = 'OU=BMS Users,DC=uno,DC=adt,DC=bms,DC=com'
filter_ea15 = '(bmsid=95450027)'

def enable_account():
    _ = modify_ldap_user(login_dirtest, modify_user_dn_dirtest, changes_enabled, None)
    #--- check it is enabled
    _ = wait_for_value(login_dirtest,search_dirtest_base,95450027,'bmsentaccountstatus',
    'Enabled',10)
    _ = wait_for_value('metaview_uat',search_dirtest_base,95450027,'bmsentaccountstatus',
    'Enabled',10)
    _ = wait_for_value(login_uno,search_base_uno,95450027,'bmsentaccountstatus',
    'Enabled',10)
    # set attrib15 flag
    print('ADD extensionAttribute15')
    _ = modify_ldap_user(login_uno, modify_user_dn_uno, changes_add_ext15, None)
    _ = wait_for_value(login_uno,search_base_uno,95450027,'extensionAttribute15',
    'TRUE',30)

def disable_account():
    _ = modify_ldap_user(login_dirtest, modify_user_dn_dirtest, changes_disabled, None)
    #--- check it is disabled - dirtest, metaview and uno dirs
    _ = wait_for_value(login_dirtest,search_dirtest_base,95450027,'bmsentaccountstatus',
    'Disabled',10)
    _ = wait_for_value('metaview_uat',search_dirtest_base,95450027,'bmsentaccountstatus',
    'Disabled',10)
    _ = wait_for_value(login_uno,search_base_uno,95450027,'bmsentaccountstatus',
    'Disabled',10)

def check_missing_attr15():
    print('check attr15')
    i = 0
    while True:
        print('.',end='',flush=True)
        _,results = ldap_search(login_uno, search_ea15, filter_ea15, search_scope, 'extensionAttribute15')
        #print(results)
        _,r = get_attr_value_if_exists(results, 'extensionAttribute15')
        #print(r)
        if (r == None) or (len(r) == 0):
            print()
            return True 
        time.sleep(2)
        i += 1
        if i >= 15:
            break
    # check one more time
    print('.',end='',flush=True)
    _,results = ldap_search(login_uno, search_ea15, filter_ea15, search_scope, 'extensionAttribute15')
    _,r = get_attr_value_if_exists(results, 'extensionAttribute15')
    if (r == None) or (len(r) == 0):
        print()
        return True 
    print()
    return False

# TO TEST:
# 1) enable account
# 2) To test JE rule where attr 15 is cleared:
#   2a) disable account, check attr15 is cleared
# 3) To test JE rule where attr 15 is not cleared:
#   3a) disable account, chekc attr15 is NOT cleared
enable_account()
#disable_account()
#r = check_missing_attr15()
#print(f'attr15 missing is {r}')
