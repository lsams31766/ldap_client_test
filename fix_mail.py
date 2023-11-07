# fix_mail.py
'''
   fix mail attribute for 2 accounts that have swapped info
'''
import sys
from ldap_client import *
from ldap3 import MODIFY_REPLACE, SUBTREE

def save_to_ldif(filename, bms_ids, dir_creds, search_base):
    # break into groups of 10, so we can save to a single ldif file
    start = 0
    end = len(bms_ids)
    step = 4
    append_file = False # first time write to file, next time appened it
    for i in range(start, end, step):
        last = i + step
        if last > end:
            last = end
        #print(f'save {i},{i+step}')
        s = '(|'
        for id in range(i,last):
            s += '(bmsid=' + bms_ids[id] + ')'
        s += ')'
        #print('->filter:',s)
        search_filter_all_users = s
        search_scope = SUBTREE
        _,results,ldif = ldap_search(dir_creds, search_base, 
           search_filter_all_users, search_scope, '*',get_ldif=True)
        ldif_to_file(filename,ldif,append_file)
        append_file = True

# now make the change
def change_mail(bms_id, new_mail, dir_creds):
    print(f'change_mail {bms_id} {new_mail} {dir_creds}')
    search_filter = '(bmsid=' + bms_id + ')'
    modify_user_dn = 'bmsid=' + bms_id + ',ou=business partners,o=bms.com'
    changes = {'mail': [(MODIFY_REPLACE, [new_mail])]}
    print(f'Change bmsid={bms_id}')
    search_scope = SUBTREE
    print(f'modify_ldap_user {modify_user_dn} {changes}')
    r = modify_ldap_user(dir_creds, modify_user_dn, changes, None)
    print(f'modify results {r}')
    # check it was changed
    _,results = ldap_search(dir_creds, search_base, search_filter, search_scope, ['mail'])
    d = result_to_dict(results)
    print(d)
    if d['mail'] != new_mail:
        print(f'ERROR mail not changed for {bms_id}')
        exit(1)
    print(f'Change for {bms_id} DONE')

dir_server = 'frds'
bmsids = ['00625201','00559111']
correct_mails = ['mustafamert.kahraman@mycro.com.tr','mert.kahraman@medismart.com.tr']
dir_creds = get_creds_from_server(dir_server)
search_base = 'o=bms.com'

#before_ldif = 'before_20231010_3.ldif'
#after_ldif = 'after_20231010_3.ldif'
#save_to_ldif(before_ldif, bmsids, dir_creds, search_base)
#cleanup_lidf_file(before_ldif)
#print(f'Before changes saved to data/{before_ldif}')
# make the changes
#  temp change
new_mail = 'mustafamerX.kahraman@mycro.com.tr'
change_mail(bmsids[0], new_mail, dir_creds)
#  change[1]
change_mail(bmsids[1], correct_mails[1], dir_creds)
#  change[0]
change_mail(bmsids[0], correct_mails[0], dir_creds)
#
# save the chagnes
#save_to_ldif(after_ldif, bmsids, dir_creds, search_base)
#cleanup_lidf_file(after_ldif)
#print(f'After changes saved to data/{after_ldif}')

