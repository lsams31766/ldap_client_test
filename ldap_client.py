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

PASSWORD='rahasak'
connection = None

def connect_ldap_server():
    global connection
    try:
        
        # Provide the hostname and port number of the openLDAP      
        server_uri = f"ldap://localhost:1389"
        server = Server(server_uri, get_info=ALL)
        # username and password can be configured during openldap setup
        connection = Connection(server,          
                                user='cn=admin,dc=rahasak,dc=com', 
                                password=PASSWORD)
        print(connection)
        bind_response = connection.bind() # Returns True or False 
        print(bind_response)
        return connection
    except LDAPBindError as e:
        connection = e

# For groups provide a groupid number instead of a uidNumber
def get_ldap_users():
    
    # Provide a search base to search for.
    search_base = 'dc=rahasak,dc=com'
    # provide a uidNumber to search for. '*" to fetch all users/groups
    #search_filter = '(uidNumber=500)'
    #search_filter = '(cn=*)'
    search_filter = '(objectClass=*)'

    # Establish connection to the server
    ldap_conn = connect_ldap_server()
    try:
        # only the attributes specified will be returned
        ldap_conn.search(search_base=search_base,       
                         search_filter=search_filter,
                         search_scope=SUBTREE, 
                         #attributes=['cn','sn','uid','uidNumber'])
                         attributes=['*'])
        # search will not return any values.
        # the entries method in connection object returns the results 
        results = connection.entries
        print(results)
    except LDAPException as e:
        results = e
        
def add_ldap_user():
# sample attributes 
    ldap_attr = {
        "cn": "Bill Doe",
        "gecos": "Do user",
        "gidNumber": '23405',
        "homeDirectory": "/home/jdoe",
        "loginShell": "/bin/bash",
        "mail": "jdoe@rahasak.com",
        "sn": '6',
        "uid": "jdoe",
        "uidNumber": '21355',
        "userPassword": b'(SSHA)asafasf'
    }

    # Bind connection to LDAP server
    ldap_conn = connect_ldap_server()

    # this will create testuser
    user_dn = "sn=6,dc=rahasak,dc=com"

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

def modify_ldap_user(): 
    
    # Bind connection to LDAP server
    ldap_conn = connect_ldap_server()
    
    # this will create testuser
    user_dn = "sn=6,dc=rahasak,dc=com"
    
    try:
        # object class for a user is inetOrgPerson
        # perform the Modify operation
        response = ldap_conn.modify(user_dn,
                         {'cn': [(MODIFY_REPLACE, ['cn-1-replaced'])],
                          'gecos': [(MODIFY_REPLACE, ['gecos-replaced'])]})
        
    except LDAPException as e:
        response = e
    print(response)
    return response   

def delete_user(): 
    
    # Bind connection to LDAP server
    ldap_conn = connect_ldap_server()
    
    # this will create testuser
    user_dn = "sn=5,dc=rahasak,dc=com"
    
    try:
        # object class for a user is inetOrgPerson
        # perform the Modify operation
        response = ldap_conn.delete(user_dn)
        
    except LDAPException as e:
        response = e
    print(response)
    return response   


if __name__ == '__main__':
    get_ldap_users()
    #add_ldap_user()
    #modify_ldap_user()
    #delete_user()
    