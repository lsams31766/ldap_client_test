'''
Created on Jul 13, 2023

@author: larry
'''

'''
TODO:
  use ed's password retrieval perl script
  move timeout code here
  get all atributes into a dict
  get 1 or more attributes for numerous servers
  can we move more of the setup parameters to this library code?
  reports for code
    - original values before script runs
    - changed values after script runs
'''

from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE
from ldap3.core.exceptions import LDAPException, LDAPBindError
import logging
logging.basicConfig(filename='client_application.log', level=logging.DEBUG)
from ldap3.utils.log import set_library_log_activation_level
set_library_log_activation_level(logging.DEBUG)
from ldap3.utils.log import set_library_log_detail_level, OFF, BASIC, NETWORK, EXTENDED
set_library_log_detail_level(BASIC)

from hosts_data import *
import json
import os
import subprocess
TERMINATE_ON_ERROR = True
import time

NC_FILENAME = 'nc.pl'
ABS_NC_FN = os.path.join(os.getcwd(),NC_FILENAME)

def get_login_info(login_creds):
    # format is list of: directory address, password, DN authentication string, port
    if type(login_creds) == str:
        #manual extaction here for now
        login_creds = login_creds.split('|')

    port = int(login_creds[3])
    if port == 389:
        server_url = "ldap://" + login_creds[0] + ":" + str(port)
    elif port == 636:
        server_url = "ldaps://" + login_creds[0] + ":" + str(port)
    # other port?  not supported yet
    else:
        print('UNKNOWN server type for port',port)
        exit(1)
    auth_password = login_creds[1]
    auth_dn = login_creds[2]
    return server_url, auth_dn, auth_password


def connect_ldap_server(login_creds):
    global connection
    server_url, auth_dn, auth_password = get_login_info(login_creds)
    # print(f"CONNECT TO {server_url} {auth_dn} {auth_password}")
    try:
        
        # Provide the hostname and port number of the openLDAP      
        server = Server(server_url, get_info=ALL)
        # username and password can be configured during openldap setup
        connection = Connection(server,          
                                user=auth_dn, 
                                password=auth_password)
        # print(connection)
        bind_response = connection.bind() # Returns True or False 
        # print(f'Connected to {server_url},  bind_response: ',bind_response)
        return connection
    except LDAPBindError as e:
        connection = e
        if TERMINATE_ON_ERROR:
            print(f'Cannot bind to {server_url}, Stopping')
            exit(1)
        
def ldap_search(login_creds, search_base, search_filter, search_scope, attrs, size_limit=5, get_ldif=False):
    # Provide a search base to search for.
    # search_base = 'dc=rahasak,dc=com'
    # provide a uidNumber to search for. '*" to fetch all users/groups
    #search_filter = '(uidNumber=500)'
    #search_filter = '(cn=*)'
    #search_filter = '(objectClass=*)'

    # Establish connection to the server
    ldap_conn = connect_ldap_server(login_creds)
    success = False
    try:
        # only the attributes specified will be returned
        ldap_conn.search(search_base=search_base,       
                         search_filter=search_filter,
                         search_scope=search_scope, 
                         attributes=attrs,
                         size_limit=size_limit)
        # the entries method in connection object returns the results 
        results = connection.entries
        if get_ldif:
            ldif = connection.response_to_ldif()
        # convert to list of dicts
        d = [json.loads(s.entry_to_json()) for s in results]
        if get_ldif:
            return True,d,ldif
        return True,d
    except LDAPException as e:
        print('Ldap Search - Failed!')
        results = e
        success = False
        if TERMINATE_ON_ERROR:
            print(f'Ldap Search {search_base} {search_filter} Failed, Stopping')
            exit(1)
    return success,results

# For groups provide a groupid number instead of a uidNumber
def get_ldap_users(login_creds, search_base, search_filter, search_scope):
        attrs = '*'
        s,r = ldap_search(login_creds, search_base, search_filter, search_scope, attrs)
        return s,r 
    
def add_ldap_user(login_creds, user_dn, ldap_attr):

    # Bind connection to LDAP server
    ldap_conn = connect_ldap_server(login_creds)
    try:
        # object class for a user is inetOrgPerson
        response = ldap_conn.add(dn=user_dn,
                                 object_class=[
                                     'top',
                                     'posixAccount',
                                    'inetOrgPerson'
                                ],
                                 attributes=ldap_attr)
    except LDAPException as e:
        response = e
        print('Add Ldap User - Failed!')
        if TERMINATE_ON_ERROR:
            print(f'Ldap Add {user_dn} {ldap_attr} Failed, Stopping')
            exit(1)
        return False, None
    print('Add Ldap User - Success')
    return True, response   

def modify_ldap_user(login_creds, modify_user_dn, changes, controls): 
    
    # Bind connection to LDAP server
    ldap_conn = connect_ldap_server(login_creds)
    try:
        response = ldap_conn.modify(modify_user_dn,changes,controls)
        
    except LDAPException as e:
        response = e
        print('Modify Ldap User - Failed!')
        if TERMINATE_ON_ERROR:
            print(f'Ldap Modify {modify_user_dn} {changes} Failed, Stopping')
            exit(1)
        return False, None
    #print('Modify Ldap User - Success')
    return True, response   

def delete_user(login_creds, delete_user_dn): 
    
    # Bind connection to LDAP server
    ldap_conn = connect_ldap_server(login_creds)
        
    try:
        response = ldap_conn.delete(delete_user_dn)
        print('Delete User - Failed!')
        return False, None
    except LDAPException as e:
        response = e
        if TERMINATE_ON_ERROR:
            print(f'Ldap Delete {delete_user_dn} Failed, Stopping')
            exit(1)
    print('Delete User - Success')
    return True, response   

def paged_search(login_creds, search_base, search_filter, search_scope, attrs, size_limit=5):
    # search for multiple entrys
    # paged search wrapped in a generator
    c = connect_ldap_server(login_creds)

    try:
        total_entries = 0
        entry_generator = c.extend.standard.paged_search(search_base = search_base,
                                                        search_filter = search_filter,
                                                        search_scope = SUBTREE,
                                                        attributes = attrs,
                                                        paged_size = 5,
                                                        generator=True)
        L = []
        for entry in entry_generator:
            total_entries += 1
            attr_value = entry.get('attributes',None)
            if attr_value:
                L.append(attr_value)
        #print(L)
        #print(f'total entries {total_entries}')
    except LDAPException as e:
        response = e
        if TERMINATE_ON_ERROR:
            print(f'Ldap multi_search Failed, Stopping')
            exit(1)
        else:
            return False, None
    return True, L

def ldap_compare(login_creds, search_dn, attrib, value):
    # look up seach_dn, attrib
    # return True if value of attrib = value
    # return False if different value or not found
    c = connect_ldap_server(login_creds)    
    try:
        r = c.compare(search_dn, attrib, value)
    except LDAPException as e:
        print(f'ldap compare exception',e)
        if TERMINATE_ON_ERROR:
            print(f'Ldap compare Failed, Stopping')
            exit(1)
        else:
            return False
    return r

#----------------------------------------------------------------
#-----------------Utility Functions------------------------------
#----------------------------------------------------------------
def item_or_list(the_item):
    # if item is single value in list, return item, otherwise return the list
    if type(the_item) == list and len(the_item) == 1:
        return the_item[0]
    return the_item

def get_attr_value_if_exists(last_response, attr_name):
    #check in list of dicts response from ldap search -
    # - does attr_name attribute exist in any of the list itmes
    # - if not return False,None,  if so return True,attr value
    ''' example:
    [
     {
        "attributes": {
            "cn": [
                "Jane Edwards"
            ],
            "gecos": [
                "JE user"
            ]
        "dn": "sn=7,ou=xxx org,c=uk,dc=rahasak,dc=com"
    }
    ]

    '''
    for attrib in last_response:
        #print(attrib.keys())
        d = attrib['attributes']
        #print(d.keys())
        if attr_name in d.keys():
            # if value is a single value in a list, return just the value
            return True, item_or_list(d[attr_name])
        return False,None

def check_attrib_matched(last_response, attr_name, attr_value):
    s,r = get_attr_value_if_exists(last_response,attr_name)
    if not s:
        return False
    return r == attr_value

def result_to_dict(last_response):
    # expect list of lenth 1, if not bail out
    #[
    #  {'attributes': 
    #     {'cn': ['Svetlana Polyanskiy'] }, 
    #     'dn': 'bmsid=00146523,ou=people,o=bms.com'
    #   }
    # ]

    if type(last_response) != list or len(last_response) != 1:
        print("results_to_dict invalid last_response format")
        return None
    # put attrs and values into a dict and return that
    # print(f'result_to_dict last_response {last_response[0].keys()}')
    d = {}
    for k in last_response[0].keys():
        item = last_response[0].get(k,None)
        if item:
            # fix all values so if they are not lists, they are single values
            if type(item) == dict:
                for key,value in item.items():
                    # print(f'result_to_dict key {key} value {value}')
                    if type(value) == list and len(value) == 1:
                        d[key] = value[0]
            else:
                d[k] = item
    return d

def get_creds_from_server(dirname):
    # get directory address, password, DN authentication string, port
    result = subprocess.run([ABS_NC_FN, dirname], stdout=subprocess.PIPE)
    l = len(result.stdout)
    fixed = str(result.stdout)[2:l+1]
    out_list = []
    params = fixed.split('|')
    for p in params:
        out_list.append(p)
    return out_list

def wait_for_value(server_creds, search_base, account_id, attrib, value, timeout, missing=False):
    # poll every 2 seconds
    if type(server_creds) == str:
        #manual extaction here for now
        server_creds = server_creds.split('|')
    server_name = server_creds[0]
    print(f'wait_for_value {server_name} - {attrib}={value}',end='',flush=True)
    number_of_polls = int(timeout / 2)
    search_filter = "(bmsid=" + str(account_id) + ")"
    # print(f'polls {number_of_polls} filter {search_filter}')
    search_scope = SUBTREE
    i = 0
    while True:
        _,results = ldap_search(server_creds, search_base, search_filter, search_scope, attrib)
        #print(results)
        print('.',end='',flush=True)
        _,r = get_attr_value_if_exists(results, attrib)
        if r == value:
            print()
            return True
        time.sleep(2)
        i += 1
        if i >= number_of_polls:
            break
    # poll one more time
    print('.',end='',flush=True)
    _,results = ldap_search(server_creds, search_base, search_filter, search_scope, attrib)
    _,r = get_attr_value_if_exists(results, attrib)
    if r != value:
        print(f'\nTIMEOUT! Did not get {attrib}={value} in {server_name}')
        exit(1)
    print()
    return True

def ldif_to_file(filename, ldif_text,append_it=False):
    # put output in local directory /data
    p = os.getcwd()
    p = p + '/data'
    if not os.path.exists(p):
        os.makedirs(p)
    filename = p + '/' + filename
    #print('FILENAME IS ',filename)
    if append_it:
        with open(filename, 'a') as f:
            f.write(ldif_text)
    else:
        with open(filename, 'w') as f:
            f.write(ldif_text)
    
def cleanup_lidf_file(filename):
    # append ldif's creates some bad lines, fix them
    # line is # total number of entries: 4version: 1
    '''clean up LDIF file:
    for each line
	    search "total number of entries:" 
	    save line number, and number of entries
    add number of entries
    first line: keep version 1
    for all other lines, delete the version line
    replace last line with total number of entries:" total amount
'''
    p = os.getcwd()
    p = p + '/data'
    filename = p + '/' + filename
    original_lines = []
    fixed_lines = []
    with open(filename,'r') as f:
        original_lines = f.readlines()
    # search for lines with "total number of entries"
    total_entries = 0
    for line in original_lines:
        pos = line.find("total number of entries:")
        #print(pos,end = ' ')
        if pos > -1:
            start = pos + len('total number of entries:')
            end = line.find("version")
            if end < 0: # not found
                end = len(line)
            total_entries += int(line[start:end])
            # do not add this line to output file
        else:
            fixed_lines.append(line) # keep the line
    fixed_lines.append(f'# total number of entries:{total_entries}\n')
    # write over the file with the corrections
    with open(filename,'w') as f:
        f.writelines(fixed_lines)

def set_terminate_on_error(value):
    global TERMINATE_ON_ERROR
    TERMINATE_ON_ERROR = value

#------------------Test Code-------------------------------------
if __name__ == '__main__':

    # TEST OF attrib to dict, wait for attrib, save ldif to file
    metaview_creds = get_creds_from_server('metaview-uat')
    search_filter = '(bmsid=00090987)'    
    search_scope = SUBTREE
    search_base_metaview  = 'o=bms.com'
    # for compare
    search_dn = 'bmsid=00090987,ou=People,o=bms.com'
    r = ldap_compare(metaview_creds, search_dn, 'mail', 'xMengping.Liu@uno.adt.bms.com')
    print(f'COMPARE returned {r}')
    s,results,ldif = ldap_search(metaview_creds, search_base_metaview, search_filter, 
        search_scope, ['*'],get_ldif=True)
    if s:
        ldif_to_file('saved_ldif.txt',ldif)
        d = result_to_dict(results)
        # print some info frm the dict
        print(f"sn: {d['sn']}, mail: {d['mail']}, id: {d['bmsid']}")

    r = wait_for_value(metaview_creds, search_base_metaview, '00090987', 
        'mail', 'Mengping.Liu@uno.adt.bms.com', 10)
    print('wait_for_value returned',r)

    # check uno
    uno_creds = get_creds_from_server('uno')
    search_base_uno = 'DC=uno,DC=adt,DC=bms,DC=com'
    search_filter = '(bmsid=95450027)'    
    attrs = ['cn','sn','uid','bmsentaccountstatus','extensionAttribute15'] 
    s,results = ldap_search(uno_creds, search_base_uno, search_filter, 
        search_scope, attrs)
    print(f'UNO got {s} {results}')

    # check enterprise uat
    enterprise_creds = get_creds_from_server('enterprise-uat')
    search_base_enterprise  = 'o=bms.com'
    search_filter = '(bmsid=00602724)'
    attrs = ['cn','sn','uid','bmsentaccountstatus','extensionAttribute15'] 
    s,results = ldap_search(uno_creds, search_base_uno, search_filter, 
        search_scope, attrs)
    print(f'Enterprise got {s} {results}')
    # get number of accounts with lotte.net in uno
    #ad_creds = "usabrbmsdct001.uno.adt.bms.com|CrasuT5Uzaq?XEt|CN=APP_JOINENGINE,OU=Service Accounts,OU=IMSS,DC=uno,DC=adt,DC=bms,DC=com|636"
    ad_creds = get_creds_from_server('adjoin-na')
    #search_base_ad  = 'DC=uno,DC=adt,DC=bms,DC=com'
    search_base_ad  = 'DC=one,DC=ads,DC=bms,DC=com'
    search_filter = '(mail=*lottebiologics.com)'
    s,results = paged_search(ad_creds, search_base_ad, search_filter, 
        search_scope, ['bmsid','userPrincipalName'])
    print(f'Number of lottebiologics.com accounts in UNO is {len(results)} items')
    for r in results:
        # print entrys with unmatched userPrincipalName
        if r['userPrincipalName'].find('lottebiologics.com') < 1:
            print(r)

    # TEST OF PAGED SEARCH
    #search_filter = '(bmsid<=95500000)'
    search_filter = '(&(bmsid>=00090848)(bmsid<=00091000))'    
    #search_filter = '(&(bmsid>=00000000)(bmsid<=00991000))'    
    # NOTE: metaview uat returns 152312 items for next filter ~ 2 minutes to retrieve
    #search_filter = '(objectClass=inetOrgPerson)'    
    search_scope = SUBTREE
    search_base_metaview  = 'o=bms.com'
    s,results = paged_search(metaview_creds, search_base_metaview, search_filter, 
        search_scope, ['bmsid'])
    print(f'paged search got {len(results)} items')
    print(results)
    exit(0)
    # Needed for connect_ldap_server
    login = 'local1389'

    # Needed for get_ldap_users
    search_base = 'dc=rahasak,dc=com'
    # provide a uidNumber to search for. '*" to fetch all users/groups
    #search_filter = '(uidNumber=500)'
    #search_filter = '(cn=*)'
    search_filter = '(objectClass=*)'
    search_scope = SUBTREE
    attrs = ['cn','uid'] 
    #success,results = ldap_search(*login, search_base, search_filter, search_scope, attrs)
    success,results = get_ldap_users(login, search_base, search_filter, search_scope)
    if success:
        print(json.dumps(results,indent=4))
    #----------------------------------------------------------------------#
    
    # for add_ldap_user
    #attributes 
    # ldap_attr = {
    #     "cn": "Jane Edwards",
    #     "gecos": "JE user",
    #     "gidNumber": '23406',
    #     "homeDirectory": "/home/jedw",
    #     "loginShell": "/bin/bash",
    #     "mail": "jedw@rahasak.com",
    #     "sn": '7',
    #     "uid": "jedw",
    #     "uidNumber": '21356',
    #     "userPassword": b'(SSHA)aspfasf'
    # }
    ldap_attr = {
        "cn": "Jane Edwards",
        "gecos": "JE user",
        "gidNumber": '23406',
        "homeDirectory": "/home/jedw",
        "loginShell": "/bin/bash",
        "mail": "jedw@rahasak.com",
        "sn": '7',
        "uid": "jedw",
        "uidNumber": '21356',
        "userPassword": b'(SSHA)aspfasf'
    }
    user_dn = "sn=7,ou=xxx org,c=uk,dc=rahasak,dc=com"
    # add_ldap_user(login, user_dn, ldap_attr)
    #----------------------------------------------------------------------#
    
    # for modify ldap user
    modify_user_dn = "sn=7,ou=xxx org,c=uk,dc=rahasak,dc=com"
    changes = {
        'cn': [(MODIFY_REPLACE, ['cn-3-replaced'])],
        'gecos': [(MODIFY_REPLACE, ['gecos-3-replaced'])]
      }
    controls = None
    # modify_ldap_user(login, modify_user_dn, changes, controls)
    #----------------------------------------------------------------------#
    
    # For delete_user
    delete_user_dn = "sn=7,ou=xxx org,c=uk,dc=rahasak,dc=com"
    # delete_user(login, delete_user_dn)
    
