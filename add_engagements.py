#add_engagements.py
''' script to add project id for users with previous project id(s)

  ...
  COMMAND LINE ARGUMENTS
  -o <project id> old project id that users are located in
  -m <project id> project id to merge (add) to the user 
  -s <filename>: Saved LDIF of the users before the changes
  -n <filename>: Saved LIDF of the users AFTER the changes

  Example:
  python add_engagements.py -o 70070 -f 76425 -a before_70070.ldif -a after_70070.ldif
'''
import sys
from ldap_client import *
from ldap3 import MODIFY_ADD, SUBTREE
import time

def print_help():
    print('''Invalid Operation:
python add_engagements.py -o <original project id> -f <final_project_id>
   -b <ldif before changes> -a <ldif after changes> 
    ''')
    print('LDIF files stored in <path_to_local_dir>/data directory')
    print('Example: python add_engagements.py -o 70070 -f 76425 -a before_70070.ldif -b after_70070.ldif')

def get_command_line_args():
    #print(f'Number of arguments:  {len(sys.argv)} arguments.') 
    #print(f'Argument List:  {str(sys.argv)}')
    # required 3 arguments, option 4th argument
    if len(sys.argv) < 5:
        print_help()
        exit(1)
    input_csv, before_ldif, after_ldif = None, None, None
    dir_server = 'enterprise'
    i = 1
    while i < len(sys.argv):
        cmd = sys.argv[i]
        val = sys.argv[i+1]
        if cmd == '-o':
            original_project_id = val
        if cmd == '-f':
            final_project_id = val
        if cmd == '-b':
            before_ldif = val
        if cmd == '-a':
            after_ldif = val 
        i += 2
    print(f'Original Project ID: {original_project_id}')
    print(f'Final Project ID: {final_project_id}')
    print(f'before ldif: {before_ldif}, after ldif: {after_ldif}')
    if None in (original_project_id, final_project_id, before_ldif, after_ldif):
        print_help()
        exit(1)
    return original_project_id, final_project_id, before_ldif, after_ldif, dir_server

def get_bmsids(project_id, dir_creds):
    # given project id, find all user's that have that project id
    search_filter = f'(bmsbpprojectid={project_id})'
    # print(f'->get_bmsids {project_id} {dir_creds} {search_filter}')
    _,results = paged_search(dir_creds, search_base_enterprise, 
            search_filter, search_scope, 'bmsid')
    d_results = result_to_dict(results)
    bms_ids = []
    for item in d_results:
        if 'bmsid' in item:
            bms_ids.append(item['bmsid'])
    return bms_ids
    
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
def make_changes(bms_ids, original_project_id, final_project_id, dir_creds):
    for bms_id in bms_ids:
        # if they already have the project id, skip them
        search_filter= f"(bmsid={bms_id})"
        v,results = ldap_search(dir_creds, search_base_enterprise, search_filter, search_scope, 'bmsbpprojectid')
        _,r = get_attr_value_if_exists(results, 'bmsbpprojectid')
        if type(r) == list:
            if (int(final_project_id) in r) or (str(final_project_id) in r):
                print(f'USER {bms_id} ALREADY HAS project id {final_project_id} - skipping')
                continue
        else: # single value
            if int(final_project_id) == int(r):
                print(f'USER {bms_id} ALREADY HAS project id {final_project_id}- skipping')
                continue
        print(f'Add project id {final_project_id} for {bms_id}')
        modify_user_dn_enterprise= f'bmsid={bms_id},ou=business partners,o=bms.com'
        add_project_id =({
            'bmsbpprojectid': [(MODIFY_ADD, [final_project_id])]
            })
        #v = modify_ldap_user(dir_creds, modify_user_dn_enterprise, add_project_id, None)
        # print('MODIFY result',v)
        # check it was changed
        v,results = ldap_search(dir_creds, search_base_enterprise, search_filter, search_scope, 'bmsbpprojectid')
        # print(v,results)
        _,r = get_attr_value_if_exists(results, 'bmsbpprojectid')
        print(f'User {bms_id} project ids {r}')

#--- COMMAND LINE PROCESSING ---#
original_project_id, final_project_id, before_ldif, after_ldif, dir_server = get_command_line_args()
dir_creds = get_creds_from_server(dir_server)
search_base_enterprise  = 'o=bms.com'
search_scope = SUBTREE
bms_ids = get_bmsids(original_project_id, dir_creds)
print(f'bmsids for {original_project_id}: {bms_ids}')

#----- MAIN CODE -----#
# save before changes to ldif file
save_to_ldif(before_ldif, bms_ids, dir_creds, search_base_enterprise)
cleanup_lidf_file(before_ldif)
print(f'Before changes saved to data/{before_ldif}')
# make the changes
make_changes(bms_ids, original_project_id, final_project_id, dir_creds)
print('Changes COMPLETE')
# save the chagnes
save_to_ldif(after_ldif, bms_ids, dir_creds, search_base_enterprise)
cleanup_lidf_file(after_ldif)
print(f'After changes saved to data/{after_ldif}')
