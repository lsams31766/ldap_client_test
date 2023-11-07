#touch_entry.py
'''
 touch entrys using bmsa attribute
 check matching bmsdsc in metasupplier, metaview, enterprise in PROD

'''
import sys
from ldap_client import *
from ldap3 import MODIFY_REPLACE, SUBTREE
import time

consultant_bmsids = [632209, 632210,
632211, 632212, 632213, 632214, 632215, 632252,	632287, 
632292, 632293, 632294, 632295,	632296,	
632360,	632255,	632271,	632272,	632275,	
632276,	632277,	632278,	632279,	632299]

business_partners_bmsids = [632216,	
632220,	632224,	632232,	632234,	632236,	632237,	
632240,	632241,	632243,	632244,	632247,	632249,	
632256,	632267,	632280,	632281,	632291,	
632297]

def pad_zeros(n):
    # make sure format is 8 digits, padd zeros as necessary
    if not n:
        return n
    s = str(n)
    s2 = s.rjust(8, '0')
    return s2

ds = {}
env = 'prod'
def make_dirs():
    global ds, env
    ds = {
    'meta-supplier': {'dir_creds':get_creds_from_server('meta-supplier'),  'search_base':'o=bms.com'},
    'metaview': {'dir_creds':get_creds_from_server('metaview'), 'search_base':'o=bms.com'},
    'enterprise': {'dir_creds':get_creds_from_server('enterprise'), 'search_base':'o=bms.com'}
    }

def touch_ids(bms_ids, is_business_partner=False):
    # modify bmsa attribute in metasupplier make it a zz
    attrib = 'bmsa'
    value = 'xx'
    dir_server = 'meta-supplier'
    for bmsid in bms_ids:
        bmsid = pad_zeros(bmsid)
        change_attrib(dir_server, bmsid, attrib, value, is_business_partner)

def check_dsc(bms_ids):
    # check bmsdsc matches in all servers - contractors
    attrib = 'bmsdsc'
    value = 'xx'
    for bmsid in bms_ids:
        bmsid = pad_zeros(bmsid)
        dir_server = 'meta-supplier'
        dir_creds = ds[dir_server]['dir_creds']
        search_base = ds[dir_server]['search_base']
        search_filter = f'(bmsid={bmsid})'
        attrs_to_get = 'bmsdsc'
        _,results = ldap_search(dir_creds, search_base, search_filter, search_scope, attrib)
        d = result_to_dict(results)
        expected_dsc = d['bmsdsc']
        print(f'in {dir_server}, {bmsid} {attrib} is {expected_dsc}')
        # check other dirs match
        check_attrib('metaview', bmsid, attrib, expected_dsc)
        check_attrib('enterprise', bmsid, attrib, expected_dsc)
        print('-------')


def check_attrib(dir_server, bmsid, attr, value):
    #print(f'ds {ds} dir_server {dir_server}')
    dir_creds = ds[dir_server]['dir_creds']
    search_base = ds[dir_server]['search_base']
    search_filter = f'(bmsid={bmsid})'
    attrs_to_get = attr
    _,results = ldap_search(dir_creds, search_base, search_filter, search_scope, attr)
    d = result_to_dict(results)
    if attr not in d:
        print(f'ERROR in check_attrib(): attrib {attr} not found in {list(d.keys())[0]}')
        print(f'last response: {d}')
        exit(1)
    if d[attr] != value:
        print(f'ERROR in check_attrib(): attrib {attr} != {value} in {list(d.keys())[0]}')
        print(f'last response: {d}')
        exit(1)
    print(f'in {dir_server}, {bmsid} {attr} is {value}')

def change_attrib(dir_server, bmsid, attrib, value, is_business_partner=False):
    print(f'change_attrib {dir_server} {bmsid} {attrib} {value}')
    dir_creds = ds[dir_server]['dir_creds']
    search_base = ds[dir_server]['search_base']		
    modify_user_dn= f'bmsid={bmsid},ou=People,o=bms.com'
    if is_business_partner:
        modify_user_dn= f'bmsid={bmsid},ou=business partners,o=bms.com'
    change_attr =({
            attrib: [(MODIFY_REPLACE, [value])]
            })
    print(f'modify_ldap_user {modify_user_dn} {change_attr}')
    v = modify_ldap_user(dir_creds, modify_user_dn, change_attr, None)
    #print('MODIFY result',v)
    # check it was changed
    search_filter = f'(bmsid={bmsid})'
    v,results = ldap_search(dir_creds, search_base, search_filter, search_scope, attrib)
    r = check_attrib_matched(results, attrib, value)
    if r == False:
        print(f'ERROR in change_attrib() could not change {attrib} to {value} in {list(ds.keys())[0]}')
        exit(0)

#-------------------main code -----------------------#
make_dirs()
search_scope = SUBTREE
#touch_ids(list(consultant_bmsids[0:1]))
#check_dsc(list(consultant_bmsids[0:1]))
#touch_ids(consultant_bmsids)
#check_dsc(consultant_bmsids)

touch_ids(list(business_partners_bmsids[0:1]),is_business_partner=True)
check_dsc(list(business_partners_bmsids[0:1]))

