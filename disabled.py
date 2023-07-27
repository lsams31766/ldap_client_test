
from ldap_client import *
from ldap3 import SUBTREE
# filter by bmsentaccountdisableddate in UNO and ONE servers

uno_creds = get_creds_from_server('uno')
search_base_uno = 'DC=uno,DC=adt,DC=bms,DC=com'
search_filter = '(bmsentaccountdisableddate=2023072* )'    
attrs = ['cn','sn','uid','bmsentaccountstatus','bmsentaccountdisableddate'] 
search_scope = SUBTREE
s,results = paged_search(uno_creds, search_base_uno, search_filter, 
    search_scope, attrs)
#print(f'UNO got {results}')
print(f'UNO got {len(results)} results')
'''
i = 1
for r in results:
    print(f'{i}-{r}')
    i += 1
'''
print('---------------------------------')
ad_creds = get_creds_from_server('adjoin-na')
search_base_ad  = 'DC=one,DC=ads,DC=bms,DC=com'
search_filter = '(bmsentaccountdisableddate=2023072*)'    
#attrs = ['cn','sn','uid','bmsentaccountstatus','bmsentaccountdisableddate'] 
attrs = ['bmsentaccountdisableddate'] 
search_scope = SUBTREE
#s,results = ldap_search(ado_creds, search_base_ad, search_filter, 
#    search_scope, attrs)
s,results = paged_search(ad_creds, search_base_ad, search_filter, 
    search_scope, attrs)
print(f'ONE got {len(results)} results')
'''
#print(f'ONE got {results}')
i = 1
for r in results:
    print(f'{i}-{r}')
    i += 1
'''

