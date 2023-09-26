#run_test_spec.py
'''
use declarative json file to run ldap test on multiple servers
sample spec file:
{"test_example.json":
  [
    {"test_name":"...", "requires":[
       {"dir_server":"xxx",
	    "criteria": [
	      {"attrib":"aaa","value":"fff"},
	      {"attrib":"aaa","value":"fff"},
	      {"attrib":"aaa","value":"fff"},
		], "change": {"dir_server":"xxx","attrib":"yyy","value":zzz"},
	    "expect": [
	       {"dir_server":"xxx","attrib":"yyy","value":zzz"},
           {"dir_server":"xxx","attrib":"yyy","value":zzz"}
	   ]
    ],
    {"test_name":"...","requires":[
       {"dir_server":"xxx","attrib":"yyy","value":zzz"},
       {"dir_server":"xxx","attrib":"yyy","value":zzz"},
	]
  ]
}

  COMMAND LINE ARGUMENTS
  -f <filenmae>: json file with test specifications
  -i <bmsid>: bmsid to run the tests on
'''
import sys
from ldap_client import *
from ldap3 import MODIFY_REPLACE, SUBTREE
import time
import openpyxl 

def print_help():
    print('''Invalid Operation:
python run_test_spec.py -f <json file> -i <bmsid> (optional: -e PROD)
    ''')
    print('Example: python run_test_spec.py -f spec.json -i 00001545')

def get_command_line_args():
    # required 2 arguments
    if len(sys.argv) < 3:
        print_help()
        exit(1)
    filename, bmsid, env = None, None, None
    i = 1
    while i < len(sys.argv):
        cmd = sys.argv[i]
        val = sys.argv[i+1]
        env = 'UAT'
        if cmd == '-f':
            filename = val
        if cmd == '-i':
            bmsid = val
        if cmd == '-e':
            env = val
        i += 2
    print(f'File: {filename}, bmsid: {bmsid}, env: {env}')
    if None in (filename, bmsid):
        print_help()
        exit(1)
    return filename, bmsid, env

def pad_zeros(n):
    # make sure format is 8 digits, padd zeros as necessary
    s = str(n)
    s2 = s.rjust(8, '0')
    return s2

ds = {}
def make_dirs():
    global ds
    if env != 'prod':
        ds = {
        'metaqa-supplier': {'dir_creds':get_creds_from_server('metaqa-supplier'),  'search_base':'o=bms.com'},
        'metaview-uat': {'dir_creds':get_creds_from_server('metaview-uat'), 'search_base':'o=bms.com'},
        'enterprise-uat': {'dir_creds':get_creds_from_server('enterprise-uat'), 'search_base':'o=bms.com'}
        }
    else:
        ds = {
        'meta-supplier': {'dir_creds':get_creds_from_server('meta-supplier'),  'search_base':'o=bms.com'},
        'metaview': {'dir_creds':get_creds_from_server('metaview'), 'search_base':'o=bms.com'},
        'enterprise': {'dir_creds':get_creds_from_server('enterprise'), 'search_base':'o=bms.com'}
        }

test = {}
def read_test_spec(filename):
    global test
    with open(filename) as f:
        s = f.read()
    # if prod, replace strings as needed
    if env == 'PROD':
        s.replace('metaqa-supplier','meta-supplier')
        s.replace('metaview-uat','metaview')
        s.replace('enterprise-uat','enterprise')

    test = json.loads(s)


def process_require(t):
    # these are attributes that need an initial value
    ''' format 
        {"dir_server":"xxx",
	     "criteria": [
	       {"attrib":"aaa","value":"fff"},
	       {"attrib":"aaa","value":"fff"},
	       {"attrib":"aaa","value":"fff"},
		 ]  
	'''
    #print(f'-->t {t}')
    dir_server = t['dir_server']
    attrs = [x['attrib'] for x in t['criteria']]
    values = [x['value'] for x in t['criteria']]
    check_attribs(dir_server, attrs, values)

def process_change(t):
    # format: {"dir_server":"xxx","attrib":"yyy","value":zzz"}
    r = change_attrib(t['dir_server'], t['attrib'], t['value'])
    if r == False:
        print(f'ERROR in process_change(): {t["attrib"]}={t["value"]} not able to be set in {t["dir_server"]}')
        exit(1)

def process_expect(t):
    ''' format
    [
	  {"dir_server":"xxx","attrib":"yyy","value":zzz"},
      {"dir_server":"xxx","attrib":"yyy","value":zzz"}
	]
    '''
    print(f'EXPECT CRITERIA: {t}')
    for item in t:
        r = wait_attr(item['dir_server'],item['attrib'],item['value'])
        if r == False:
            print(f'ERROR in process_expect(): {item["attrib"]}={item["value"]} not found in {item["dir_server"]}')
            exit(1)

def check_attribs(dir_server, attrs, values):
    #print(f'ds {ds} dir_server {dir_server}')
    dir_creds = ds[dir_server]['dir_creds']
    search_base = ds[dir_server]['search_base']
    search_filter = f'(bmsid={bmsid})'
    attrs_to_get = ','.join(attrs)
    _,results = ldap_search(dir_creds, search_base, search_filter, search_scope, attrs)
    d = result_to_dict(results)
    for i in range(len(attrs)):
        if attrs[i] not in d:
            print(f'ERROR in check_attribs(): attrib {attrs[i]} not found in {list(ds.keys())[0]}')
            print(f'last response: {d}')
            exit(1)
        if d[attrs[i]] != values[i]:
            print(f'ERROR in check_attribs(): attrib {attrs[i]} != {values[i]} in {list(ds.keys())[0]}')
            print(f'last response: {d}')
            exit(1)

def wait_attr(dir_server, attr, value):
    # wait for value set with timeout
    dir_creds = ds[dir_server]['dir_creds']
    search_base = ds[dir_server]['search_base']
    search_filter = f'(bmsid={bmsid})'
    r = wait_for_value(dir_creds, search_base, bmsid, attr, value, 60)
    if r == False:
        print('ERR wait_attr TIMEOUT waiting for {attr}={value}')

def change_attrib(dir_server, attrib, value):
    dir_creds = ds[dir_server]['dir_creds']
    search_base = ds[dir_server]['search_base']		 
    modify_user_dn= f'bmsid={bmsid},ou=People,o=bms.com'
    change_attr =({
	    attrib: [(MODIFY_REPLACE, [value])]
	    })
    v = modify_ldap_user(dir_creds, modify_user_dn, change_attr, None)
    print('MODIFY result',v)
    # check it was changed
    search_filter = f'(bmsid={bmsid})'
    v,results = ldap_search(dir_creds, search_base, search_filter, search_scope, attrib)
    r = check_attrib_matched(results, attrib, value)
    if r == False:
        print(f'ERROR in change_attrib() could not change {attrib} to {value} in {list(ds.keys())[0]}')
        exit(0)

def set_initial_conditions(requires):
    for r in requires['criteria']:
        change_attrib(requires['dir_server'], r['attrib'], r['value'])
    # check everythin is set in all dirs
    search_filter = f'(bmsid={bmsid})'
    for r in requires['criteria']:
        for ds_name in ['metaqa-supplier','metaview-uat','enterprise-uat']:
            search_base = ds[ds_name]['search_base']		 
            _ = wait_for_value(ds[ds_name]['dir_creds'], 
                search_base, bmsid, r['attrib'], r['value'], 30)
    

def run_test():
    test_name = list(test.keys())[0]
    print(f'using file: {test_name}')
    print(f'test keys {test.keys()}')
    for t in test[test_name]:
        print(f'Starting test: {t["test_name"]}')
        set_initial_conditions(t['requires'])
        #process_require(t['requires'])
        #print(f't keys {t.keys()}')
        process_change(t['change'])
        process_expect(t['expect'])
    print('DONE')

make_dirs()
filename, bmsid, env = get_command_line_args()
bmsid = pad_zeros(bmsid)
search_scope = SUBTREE

read_test_spec(filename) #creates test dictionary
run_test()
