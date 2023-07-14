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


def connect_ldap_server(server_url, auth_dn, auth_password):
    global connection
    try:
        
        # Provide the hostname and port number of the openLDAP      
        server = Server(server_url, get_info=ALL)
        # username and password can be configured during openldap setup
        connection = Connection(server,          
                                user=auth_dn, 
                                password=auth_password)
        print(connection)
        bind_response = connection.bind() # Returns True or False 
        print(bind_response)
        return connection
    except LDAPBindError as e:
        connection = e

# For groups provide a groupid number instead of a uidNumber
def get_ldap_users(server_url, auth_dn, auth_password, search_base, search_filter, search_scope):
    
    # Provide a search base to search for.
    # search_base = 'dc=rahasak,dc=com'
    # provide a uidNumber to search for. '*" to fetch all users/groups
    #search_filter = '(uidNumber=500)'
    #search_filter = '(cn=*)'
    #search_filter = '(objectClass=*)'

    # Establish connection to the server
    ldap_conn = connect_ldap_server(server_url, auth_dn, auth_password)
    try:
        # only the attributes specified will be returned
        ldap_conn.search(search_base=search_base,       
                         search_filter=search_filter,
                         search_scope=search_scope, 
                         attributes=['cn','sn','uid','uidNumber','extensionAttribute15','bmsentaccountstatus'])
                         #attributes=['*'])
        # search will not return any values.
        # the entries method in connection object returns the results 
        results = connection.entries
        print(results)
    except LDAPException as e:
        results = e
        
def add_ldap_user(server_url, auth_dn, auth_password, user_dn, ldap_attr):

    # Bind connection to LDAP server
    ldap_conn = connect_ldap_server(server_url, auth_dn, auth_password)

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
    print(response)
    return response   

def modify_ldap_user(server_url, auth_dn, auth_password, modify_user_dn, changes, controls): 
    
    # Bind connection to LDAP server
    ldap_conn = connect_ldap_server(server_url, auth_dn, auth_password)
        
    try:
        # object class for a user is inetOrgPerson
        # perform the Modify operation
        response = ldap_conn.modify(modify_user_dn,changes,controls)
        
    except LDAPException as e:
        response = e
    print(response)
    return response   

def delete_user(server_url, auth_dn, auth_password, delete_user_dn): 
    
    # Bind connection to LDAP server
    ldap_conn = connect_ldap_server(server_url, auth_dn, auth_password)
        
    try:
        # object class for a user is inetOrgPerson
        # perform the Modify operation
        response = ldap_conn.delete(delete_user_dn)
        
    except LDAPException as e:
        response = e
    print(response)
    return response   


if __name__ == '__main__':
    # Needed for connect_ldap_server
    server_url = hosts_data['local1389'][HD_URL]
    auth_dn = hosts_data['local1389'][HD_DN]
    auth_password = hosts_data['local1389'][HD_PW]

    # Needed for get_ldap_users
    search_base = 'dc=rahasak,dc=com'
    # provide a uidNumber to search for. '*" to fetch all users/groups
    #search_filter = '(uidNumber=500)'
    #search_filter = '(cn=*)'
    search_filter = '(objectClass=*)'
    search_scope = SUBTREE
    get_ldap_users(server_url, auth_dn, auth_password, search_base, search_filter, search_scope)
    #----------------------------------------------------------------------#
    
    # for add_ldap_user
    #attributes 
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
    user_dn = "sn=7,dc=rahasak,dc=com"
    # add_ldap_user(server_url, auth_dn, auth_password, user_dn, ldap_attr)
    #----------------------------------------------------------------------#
    
    # for modify ldap user
    modify_user_dn = "sn=6,dc=rahasak,dc=com"
    changes = {
        'cn': [(MODIFY_REPLACE, ['cn-3-replaced'])],
        'gecos': [(MODIFY_REPLACE, ['gecos-3-replaced'])]
      }
    controls = None
    #modify_ldap_user(server_url, auth_dn, auth_password, modify_user_dn, changes, controls)
    #----------------------------------------------------------------------#
    
    # For delete_user
    delete_user_dn = "sn=7,dc=rahasak,dc=com"
    # delete_user(server_url, auth_dn, auth_password, delete_user_dn)
    
