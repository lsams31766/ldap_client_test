from ldap_client import *
from ldap3 import MODIFY_ADD
import json
import time

# Needed for connect_ldap_server
login = 'local1389'

search_base = 'dc=rahasak,dc=com'
search_filter = '(sn=7)'
search_scope = SUBTREE
attrs = ['*']
success,results = ldap_search(login, search_base, search_filter, search_scope, attrs)
if success:
    print('FOUND sn=7:')
    print(json.dumps(results,indent=4))
# TEST ADDING an Attribute
modify_user_dn = "sn=7,ou=xxx org,c=uk,dc=rahasak,dc=com"
changes_add_bms_a = {
    'bms_a': [(MODIFY_ADD, [])]
    }

changes = {
        'cn': [(MODIFY_REPLACE, ['cn-3-replaced'])],
        'gecos': [(MODIFY_REPLACE, ['gecos-3-replaced'])]
      }

controls = None
#s = modify_ldap_user(login, modify_user_dn, changes_add_bms_a, controls)
# check it was added
#s = check_attrib_matched(results, 'bms_a', 'TRUE')
#print('attrib was added:',s)

# find an attribute
s,r = get_attr_value_if_exists(results, 'mail')
if s:
    print('mail attr found is:',r)
# see if matches expected
s = check_attrib_matched(results, 'mail', 'jedw@rahasak.com')
print('mail is jedw@rahasak.com: ',s)
s = check_attrib_matched(results, 'mail', 'jedw@rahasak2.com')
print('mail is jedw@rahasak2.com: ',s)
# inversion
if r == 'jedw@rahasak.com':
    new_mail = 'jedw@rahasak2.com'
else:
    new_mail = 'jedw@rahasak.com'
print('CHANGE mail to ',new_mail)

# now change the mail and check again
modify_user_dn = "sn=7,ou=xxx org,c=uk,dc=rahasak,dc=com"
changes = {
    'mail': [(MODIFY_REPLACE, [new_mail])]
    }
controls = None
s = modify_ldap_user(login, modify_user_dn, changes, controls)
# check it changed
success,results = ldap_search(login, search_base, search_filter, search_scope, attrs)
s = check_attrib_matched(results, 'mail', 'jedw@rahasak.com')
print('mail is jedw@rahasak.com: ',s)
s = check_attrib_matched(results, 'mail', 'jedw@rahasak2.com')
print('mail is jedw@rahasak2.com: ',s)

