#change_managers.py
''' script to change managers for a group of users
  requires a CSV - File format:
  ID,Manager ID
  00010000,0100010
  00010000,0100010
  00010000,0100010
  ...
  COMMAND LINE ARGUMENTS
  -i <filenmae>: Input CSV file of User Id's and their NEW manager ID's
  -s <filename>: Saved LDIF of the users before the changes
  -n <filename>: Saved LIDF of the users AFTER the changes
  -d <directory>: Directory server - default is Enteprise Prod
'''
import sys
from ldap_client import *
from ldap3 import MODIFY_REPLACE, SUBTREE
import time

def print_help():
    print('''Invalid Operation:
python3 change_managers.py -i<input csv fiename> -b <ldif before changes> 
    -a <ldif after changes> (OPTIONAL: -d <directory server name ie... enterprise>)
    ''')
    print('Example: p1.csv p1_before.ldif p2_after.ldif')

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
    manager_ids = []
    for line in lines:
        line = line.strip()
        line_split = line.split(',')
        if 'id' in line_split[0].lower():
            pass
        else:
            ids.append(line_split[0])
            manager_ids.append(line_split[1])
    return ids,manager_ids

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
        print('->filter:',s)
        search_filter_all_users = s
        search_scope = SUBTREE
        _,results,ldif = ldap_search(dir_creds, search_base, 
           search_filter_all_users, search_scope, '*',get_ldif=True)
        ldif_to_file(filename,ldif,append_file)
        append_file = True

input_csv, before_ldif, after_ldif, dir_server = get_command_line_args()
ids, manager_ids = get_changes_from_csv_file(input_csv)
#print(ids,manager_ids)
dir_creds = get_creds_from_server(dir_server)
if dir_server == 'enterprise':
    search_base_enterprise  = 'o=bms.com'
else:
    print('SERVER not supported yet')
    exit(1)
search_scope = SUBTREE
search_filter = []
modify_user_dn_enterprise = []
changes_manager = []
# save before changes to ldif file
save_to_ldif(before_ldif, ids, dir_creds, search_base_enterprise)
cleanup_lidf_file(before_ldif)