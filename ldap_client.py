'''
Created on Jul 13, 2023

@author: larry
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
TERMINATE_ON_ERROR = True


def get_login_info(login_name):
    server_url = hosts_data[login_name][0]
    auth_dn = hosts_data[login_name][1]
    login_name_fixed = login_name.upper() + '_PASSWORD'
    auth_password = os.environ[login_name_fixed]
    return server_url, auth_dn, auth_password


def connect_ldap_server(login_name):
    global connection
    server_url, auth_dn, auth_password = get_login_info(login_name)
    try:
        
        # Provide the hostname and port number of the openLDAP      
        server = Server(server_url, get_info=ALL)
        # username and password can be configured during openldap setup
        connection = Connection(server,          
                                user=auth_dn, 
                                password=auth_password)
        # print(connection)
        bind_response = connection.bind() # Returns True or False 
        print(f'Connected to {server_url},  bind_response: ',bind_response)
        return connection
    except LDAPBindError as e:
        connection = e
        if TERMINATE_ON_ERROR:
            print(f'Cannot bind to {server_url}, Stopping')
            exit(1)
        
def ldap_search(login_name, search_base, search_filter, search_scope, attrs):
    # Provide a search base to search for.
    # search_base = 'dc=rahasak,dc=com'
    # provide a uidNumber to search for. '*" to fetch all users/groups
    #search_filter = '(uidNumber=500)'
    #search_filter = '(cn=*)'
    #search_filter = '(objectClass=*)'

    # Establish connection to the server
    ldap_conn = connect_ldap_server(login_name)
    success = False
    try:
        # only the attributes specified will be returned
        ldap_conn.search(search_base=search_base,       
                         search_filter=search_filter,
                         search_scope=search_scope, 
                         attributes=attrs)
        # the entries method in connection object returns the results 
        results = connection.entries
        # convert to list of dicts
        d = [json.loads(s.entry_to_json()) for s in results]
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
def get_ldap_users(login_name, search_base, search_filter, search_scope):
        attrs = '*'
        s,r = ldap_search(login_name, search_base, search_filter, search_scope, attrs)
        return s,r 
    
def add_ldap_user(login_name, user_dn, ldap_attr):

    # Bind connection to LDAP server
    ldap_conn = connect_ldap_server(login_name)
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

def modify_ldap_user(login_name, modify_user_dn, changes, controls): 
    
    # Bind connection to LDAP server
    ldap_conn = connect_ldap_server(login_name)
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

def delete_user(login_name, delete_user_dn): 
    
    # Bind connection to LDAP server
    ldap_conn = connect_ldap_server(login_name)
        
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


#------------------Test Code-------------------------------------
if __name__ == '__main__':
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
    
