#add_project_id.py
''' script to add project id's for a group of users
  the bmsbpprojectid attribute has values added to it (or created if not exists)

  requires a CSV - File format:
  BMSID,Add-bmsbpprojectid,cn,uid
  00620206,79149,Ambre Monfort,monfora1
  00620140,79149,Antoinette Burriss,burrisf1
  ...

  COMMAND LINE ARGUMENTS
  -i <filenmae>: Input CSV file of User Id's and their project ID's
  -s <filename>: Saved LDIF of the users before the changes
  -n <filename>: Saved LIDF of the users AFTER the changes
  -d <directory>: Directory server - default is Enteprise Prod
'''
import sys
from ldap_client import *
from ldap3 import MODIFY_ADD, SUBTREE
import time

def print_help():
    print('''Invalid Operation:
python3 add_project_id.py -i<input csv fiename> -b <ldif before changes> 
    -a <ldif after changes> (OPTIONAL: -d <directory server name ie... enterprise>)
    ''')
    print('LDIF files stored in <path_to_local_dir>/data directory')
    print('Example: python3 add_project-id.py p1.csv p1_before.ldif p2_after.ldif')

def get_command_line_args():
    #print(f'Number of arguments:  {len(sys.argv)} arguments.') 
    #print(f'Argument List:  {str(sys.argv)}')
    # required 3 arguments, option 4th argument
    if len(sys.argv) < 4:
        print_help()
        exit(1)
    input_csv, before_ldif, after_ldif = None, None, None
    dir_server = 'enterprise'
    i = 1
    while i < len(sys.argv):
        cmd = sys.argv[i]
        val = sys.argv[i+1]
        if cmd == '-i':
            input_csv = val
        if cmd == '-b':
            before_ldif = val
        if cmd == '-a':
            after_ldif = val 
        if cmd == '-d': 
            dir_server = val
        i += 2
    print(f'Input File: {input_csv}, before ldif: {before_ldif}')
    print(f'after ldif: {after_ldif}, dir server: {dir_server}')
    if None in (input_csv, before_ldif, after_ldif):
        print_help()
        exit(1)
    return input_csv, before_ldif, after_ldif, dir_server

def get_changes_from_csv_file(input_csv):
    with open(input_csv,'r') as f1:
        lines = f1.readlines()
    ids = []
    project_ids = []
    for line in lines:
        line = line.strip()
        line_split = line.split(',')
        if 'bmsid' in line_split[0].lower():
            pass
        else:
            # some lines have 2 project ids: 00619831,75026;79149,Angela Gibbs,gibbsa4
            # break this into 2 entrys, so all the projects get add
            if line.find(';') > 0:
                ids.append(line_split[0])
                ids.append(line_split[0])
                p = line_split[1]
                project_ids.append(p.split(';')[0])
                project_ids.append(p.split(';')[1])
            else: # single project id on line
                ids.append(line_split[0])
                project_ids.append(line_split[1])
    return ids,project_ids

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
def make_changes(bms_ids, project_ids, dir_creds):
    search_filter = []
    modify_user_dn_enterprise = []
    add_project_ids = []
    for i in range(len(bms_ids)):
        p = project_ids[i]
        if p.find(';') > 0:
            p = p.split(';')[0]
        search_filter.append('(bmsid=' + bms_ids[i] + ')')
        modify_user_dn_enterprise.append('bmsid=' + bms_ids[i] + ',ou=business partners,o=bms.com')
        add_project_ids.append({
            'bmsbpprojectid': [(MODIFY_ADD, [project_ids[i]])]
            })

    for i in range(len(bms_ids)):
        search_scope = SUBTREE
        # if they already have the project id, skip them
        v,results = ldap_search(dir_creds, search_base_enterprise, search_filter[i], search_scope, 'bmsbpprojectid')
        _,r = get_attr_value_if_exists(results, 'bmsbpprojectid')
        if type(r) == list:
            if (int(project_ids[i]) in r) or (str(project_ids[i]) in r):
                print(f'USER {bms_ids[i]} ALREADY HAS project id - skipping')
                continue
        else: # single value
            if int(project_ids[i]) == int(r):
                continue

        print(f'Add project id {add_project_ids[i]} for {modify_user_dn_enterprise[i]}')
        v = modify_ldap_user(dir_creds, modify_user_dn_enterprise[i], add_project_ids[i], None)
        # print('MODIFY result',v)
        # check it was changed
        v,results = ldap_search(dir_creds, search_base_enterprise, search_filter[i], search_scope, 'bmsbpprojectid')
        # print(v,results)
        _,r = get_attr_value_if_exists(results, 'bmsbpprojectid')
        print(f'User {bms_ids[i]} project ids {r}')

#--- COMMAND LINE PROCESSING ---#
input_csv, before_ldif, after_ldif, dir_server = get_command_line_args()
ids, project_ids = get_changes_from_csv_file(input_csv)
#print(ids,manager_ids)
dir_creds = get_creds_from_server(dir_server)
if dir_server == 'enterprise':
    search_base_enterprise  = 'o=bms.com'
else:
    print(f'SERVER {dir_server} not supported yet')
    exit(1)

#----- MAIN CODE -----#
# save before changes to ldif file
# print("CLA's",input_csv, before_ldif, after_ldif, dir_server)
# print("input data")
#print(ids)
#print(project_ids)
# print("dir creds",dir_creds)
#for i in range(len(ids)):
#    print(f'{ids[i]},{project_ids[i]}')

save_to_ldif(before_ldif, ids, dir_creds, search_base_enterprise)
cleanup_lidf_file(before_ldif)
print(f'Before changes saved to data/{before_ldif}')
# make the changes
make_changes(ids, project_ids, dir_creds)
print('Changes COMPLETE')
# save the chagnes
save_to_ldif(after_ldif, ids, dir_creds, search_base_enterprise)
cleanup_lidf_file(after_ldif)
print(f'After changes saved to data/{after_ldif}')
