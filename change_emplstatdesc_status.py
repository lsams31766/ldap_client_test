#change_emplstatdesc_status.py
''' script to change bmshremplstatdesc and bmsemployeestatus for set of people
  ...
  COMMAND LINE ARGUMENTS
  -b <filename>: Saved LDIF of the users before the changes
  -a <filename>: Saved LIDF of the users AFTER the changes
'''
import sys
from ldap_client import *
from ldap3 import MODIFY_REPLACE, SUBTREE
import time
import openpyxl 

def print_help():
    print('''Invalid Operation:
python3 change_emplstatdesc_status.py -b <ldif before changes> 
    -a <ldif after changes> 
    ''')
    print('LDIF files stored in <path_to_local_dir>/data directory')
    print('Example: python3 change_emplstatdesc_status.py -b p1_before.ldif -a p2_after.ldif')

def get_command_line_args():
    #print(f'Number of arguments:  {len(sys.argv)} arguments.') 
    #print(f'Argument List:  {str(sys.argv)}')
    # required 3 arguments
    if len(sys.argv) < 3:
        print_help()
        exit(1)
    before_ldif, after_ldif = None, None
    dir_server = 'meta-supplier'
    i = 1
    while i < len(sys.argv):
        cmd = sys.argv[i]
        val = sys.argv[i+1]
        if cmd == '-b':
            before_ldif = val
        if cmd == '-a':
            after_ldif = val 
        i += 2
    print(f'before ldif: {before_ldif}')
    print(f'after ldif: {after_ldif}, dir server: {dir_server}')
    if None in (before_ldif, after_ldif):
        print_help()
        exit(1)
    return before_ldif, after_ldif, dir_server

def pad_zeros(n):
    # make sure format is 8 digits, padd zeros as necessary
    s = str(n)
    s2 = s.rjust(8, '0')
    return s2

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
def make_changes(bms_ids, dir_creds):
    search_filter = []
    modify_user_dn = []
    changes = []
    for i in range(len(bms_ids)):
        search_filter.append('(bmsid=' + bms_ids[i] + ')')
        modify_user_dn.append('bmsid=' + bms_ids[i] + ',ou=People,o=bms.com')
        #changes.append({
        #    'bmshremplstatdesc': [(MODIFY_REPLACE, ['Withdrawn'])],
        #    'bmsemployeestatus': [(MODIFY_REPLACE, ['Terminated'])],
        #    })
        changes.append({
            'bmsemployeestatus': [(MODIFY_REPLACE, ['Terminated'])]
            })

    for i in range(len(bms_ids)):
        print(f'Change bmsid={bms_ids[i]}')
        search_scope = SUBTREE
        _ = modify_ldap_user(dir_creds, modify_user_dn[i], changes[i], None)
        # check it was changed
        _,results = ldap_search(dir_creds, search_base, search_filter[i], search_scope, ['bmshremplstatdesc','bmsemployeestatus'])
        d = result_to_dict(results)
        #if d['bmshremplstatdesc'] != 'Withdrawn':
        #    print(f'ERROR bmshremplstatdesc not Withdrown for {bms_ids[i]}')
        #    exit(1)
        if d['bmsemployeestatus'] != 'Terminated':
            print(f'ERROR bmsemployeestatus not Terminated for {bms_ids[i]}')
            exit(1)
        print(f'Change for {bms_ids[i]} DONE')


#--- COMMAND LINE PROCESSING ---#
before_ldif, after_ldif, dir_server = get_command_line_args()
#ids = ['00616280']
#ids = ['00625414', '00624007', '00624179', '00625358']
ids = ['00627555']
dir_creds = get_creds_from_server(dir_server)
search_base = 'o=bms.com'

#----- MAIN CODE -----#
# save before changes to ldif file
save_to_ldif(before_ldif, ids, dir_creds, search_base)
cleanup_lidf_file(before_ldif)
print(f'Before changes saved to data/{before_ldif}')
# make the changes
make_changes(ids, dir_creds)
print('Changes COMPLETE')
# save the chagnes
save_to_ldif(after_ldif, ids, dir_creds, search_base)
cleanup_lidf_file(after_ldif)
print(f'After changes saved to data/{after_ldif}')

