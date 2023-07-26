from ldap_client import *
from ldap3 import MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE, SUBTREE
import time

#UAT
# directory address, password, DN authentication string, port
metaview_creds = "metaview-uat.bms.com|cpjevkstag|cn=join engine,ou=nonpeople,o=bms.com|389"
ad_creds = "usabrbmsdct001.uno.adt.bms.com|CrasuT5Uzaq?XEt|CN=APP_JOINENGINE,OU=Service Accounts,OU=IMSS,DC=uno,DC=adt,DC=bms,DC=com|636"
search_base_ad  = 'DC=uno,DC=adt,DC=bms,DC=com'
search_filter = '(bmsid=95450027)'
search_scope = SUBTREE
search_base_metaview  = 'o=bms.com'

# PROD
#metaview_creds = get_creds_from_server('metaview')
#search_base_metaview  = 'o=bms.com'
#ad_creds = get_creds_from_server('adjoin-na')
#search_base_ad  = 'DC=one,DC=ads,DC=bms,DC=com'

# change mail in ad
# read value of UserPrincpalName make sure it follows the je rules

# UAT RULES
# if mail is bms.com -> UPN gets %user%<L>@uno.adt.bms.com
# if mail is lotte.net OR lottebiologics.com -> UPN gets %LINKED.mail% 
# default -> UPN gets %uid%<L>@uno.adt.bms.com

#get current mail for the user
# save mail to restore later
original_mail_value = 'adriana.baldassarre@uno.adt.bms.com'

# change to lotte.net
#new_mail = 'adriana.baldassarre@lotte.net'
new_mail = 'adriana.baldassarre@lottebiologics.com' 
print(f'CHANGE mail in metaview to {new_mail}')
modify_user_dn_metaview =  'bmsid=95450027,ou=People,o=bms.com'
modify_user_dn_ad =  'CN=Baldassarre\, Adriana (95450027),OU=BMS Users,DC=uno,DC=adt,DC=bms,DC=com'

changes_mail =  {
        'mail': [(MODIFY_REPLACE, new_mail)],
        }
r = modify_ldap_user(ad_creds, modify_user_dn_ad, changes_mail, None)
#r = modify_ldap_user(metaview_creds, modify_user_dn_metaview, changes_mail, None)
print(f'------> result from modify: {r}')
_,results = ldap_search(metaview_creds, search_base_metaview, search_filter, search_scope, ['mail'])
print(results)
_,r = get_attr_value_if_exists(results, 'mail')
print(f'METAVIEW: mail search got {r}')



_,results = ldap_search(ad_creds, search_base_ad, search_filter, search_scope, ['mail'])
print('UNO',results)
_,r = get_attr_value_if_exists(results, 'mail')
print(f'UNO: mail search got {r}')

_,results = ldap_search(ad_creds, search_base_ad, search_filter, search_scope, ['userPrincipalName'])
print('UNO',results)
_,r = get_attr_value_if_exists(results, 'userPrincipalName')
print(f'UNO: userPrincipalName search got {r}')

exit(0)

_,results = ldap_search(metaview_creds, search_base_metaview, search_filter, search_scope, ['mail'])
print(results)
_,r = get_attr_value_if_exists(results, 'mail')
print(f'METAVIEW: mail search got {r}')

_,results = ldap_search(metaview_creds, search_base_metaview, search_filter,
   search_scope, ['userPrincipalName'])
print(results)
_,r = get_attr_value_if_exists(results, 'userPrincipalName')
print(f'METAVIEW: userPrincipalName search got {r}')

