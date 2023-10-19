import sys
from ldap_client import *
from ldap3 import SUBTREE,DEREF_ALWAYS
import json
from collections import defaultdict

'''
   search strategy (search for all rules invloving an attribute)
   1) Get the attribute we are interested in
   2) Get the rule name, from/to mappings for the attribute
   3) Join attribute flow rules with the rule names - to get all flow rules
   4) Get any constructed attributes included in any of the mappings
   5) Get the consturecte attribute rules for the found construected attributes
   6) Display data:
      attribute name
      From source.attribute To destination.attribute - Flow Rule name
         Flow rule critiera

'''

def print_help():
    print('''Invalid Operation:
python je_rules_search.py -a <attribute name> -c <connector (optional)> -d <tomv or tocv (optional)> -r <rule_name (optional)> -e <prod default, uat>
-C (optional, show all connectors)
-A (optional show all attributes)
-K <attribute name> (optional, show all constructed attributes, related to attribute_name )
    ''')

d_cmd_args = {}
def get_command_line_args():
    global d_cmd_args
    if len(sys.argv) < 2:
        print_help()
        exit(1)
    i = 1
    d_cmd_args = {}
    cmd_map1 = {'a':'attribute','c':'connector','d':'direction',
    'r':'rule_name','e':'env'}
    cmd_map2 = {'C':'show_connectors','A':'show_attributes',
    'K':'show_constructed_attributes'}
    while i < len(sys.argv):
        cmd = sys.argv[i].replace('-','')
        if cmd in cmd_map1: # has a val
            val = sys.argv[i+1]
            d_cmd_args[cmd_map1[cmd]] = val
            i += 2
            continue
        if cmd in cmd_map2: # does not have a val
            d_cmd_args[cmd_map2[cmd]] = True
            i += 1
            continue
        print_help() # cmd not found - stop
        exit(1)

def clean_rule_name(s):
    # take out text after space
    s_split = s.split(' ')
    return (s_split[0])    

def get_mapping_rules_and_mappings(login_creds):
    if 'attribute' not in d_cmd_args:
        print('ERROR cannot find mapping rules with no attribute selected')
        exit(1)
    search_text = d_cmd_args['attribute']
    cns = []
    search_base = 'cn=Configurations,cn=Attribute Flow,cn=Shared Configuration,cn=JoinEngine Configuration,ou=InJoinv8,ou=Config,o=bms.com'
    search_filter = '(cn=*)'
    attrs = ['cn','mdsattributemappingpairs','mdsattributeflowselectioncriteria','mdsdisplayname','mdsattributeflowdirection','mdsgeneralconfiguration']
    _,results = paged_search(login_creds, search_base, search_filter, search_scope, attrs,dereference_aliases=DEREF_ALWAYS)
    d_rule_mappings={}
    # print(f'SEARCH for {search_text} in attr mdsattributemappingpairs in {search_base}')
    d_results = result_to_dict(results)
    for flow_item in d_results:
        if 'mdsdisplayname' in flow_item:
            rule_name = flow_item['mdsdisplayname']
        else:
            rule_name = clean_rule_name(flow_item['cn'][0])
        if 'mdsattributemappingpairs' in flow_item:
            pairs = flow_item['mdsattributemappingpairs']
            found = False
            for p in pairs:
                if (search_text.lower() in p.lower()) and (found == False):
                    found = True
                    p_split = p.split(' ')
                    p_from = p_split[0].lower()
                    p_to = p_split[1].lower()
                    # print(f'FOUND {p_from}-->{p_to} in {rule_name}')
                    if rule_name not in d_rule_mappings:
                        d_rule_mappings[rule_name] = [{'mapping':(p_from,p_to)}]
                        d_rule_mappings[rule_name].append({'direction':flow_item['mdsattributeflowdirection']})
                        d_rule_mappings[rule_name].append({'from_to':flow_item['mdsgeneralconfiguration']})
                    else:
                        d_rule_mappings[rule_name].append({'mapping':(p_from,p_to)})
                    if 'mdsattributeflowselectioncriteria' in flow_item:
                        criteria = flow_item['mdsattributeflowselectioncriteria']
                        d_rule_mappings[rule_name].append({'flow_criteria':criteria})
            
    return d_rule_mappings # {'rule1':(from,to),'rule2':(from,to)...}

def get_flow_rules(login_creds, d_rule_mappings):
    # get the rules we need
    search_base = 'cn=DN Mapping Rules,cn=Shared Configuration,cn=JoinEngine Configuration,ou=InJoinv8,ou=Config,o=bms.com'
    search_filter = '(objectClass=*)'
    # get all mappings so we can search for an attribute
    attrs = ['cn','mdsgeneralconfiguration','mdsgenericrulerequirements','mdsgenericrulesubstitution']
    _,results = paged_search(login_creds, search_base, search_filter, search_scope, attrs)
    #print(f'\nSEARCH for {attrs} in attr mdsattributemappingpairs in {search_base}\n')
    for rule in results:
        rule_name = rule['cn'][0]
        #print(rule_name)
        if rule_name in d_rule_mappings:
            #print(rule)
            d_rule_mappings[rule_name].append({'config':rule['mdsgeneralconfiguration']})
            d_rule_mappings[rule_name].append({'requires':rule['mdsgenericrulerequirements']})
            d_rule_mappings[rule_name].append({'output':rule['mdsgenericrulesubstitution']})

def clean_server_name(raw_server):
    # remove LDAP://  remove MDSDB:// remove /DC=... 
    fixed_server = raw_server.replace('LDAP://','')
    fixed_server = fixed_server.replace('MDSDB://','')
    # remove any thing passed 3 char from / charachter on
    p = fixed_server.find('/',7)
    if p > 6:
        fixed_server = fixed_server[0:p]
    return fixed_server

def get_connector_from_address(server_addr):
    if server_addr.find('metaview') >= 0:
        return 'MV'
    print(f'-->search for {server_addr}')
    for connector,v in d_connectors.items():
        if clean_server_name(v['server']) == server_addr:
            return connector
    return 'UKNOWN connector'

def get_short_con_name(long_connector_name):
    # if given long connector name, return short name
    for connector,v in d_connectors.items():
        if v['description'] == long_connector_name:
            return connector
    # not found, return original name
    return long_connector_name

def clean_from_to(from_to,rule_name):
    # user rule name, OR servers found
    # find TO or to
    if ('to' in rule_name) or ('To' in rule_name):
        if 'to' in rule_name:
            rule_split = rule_name.split('to')
        else:
            rule_split = rule_name.split('To')
        c_from = get_short_con_name(rule_split[0])
        if '-' in rule_split[1]:
            c_to_split = rule_split[1].split('-')
        else:
            c_to_split = rule_split[1].split('_')
        c_to = get_short_con_name(c_to_split[0])
        return(f'{c_from}-->{c_to}')
    #given from server, to server, replace with connector names
    #input format: ['SourceDataServer=LDAP://metaview-uat.bms.com', 'DestzinationDataServer=LDAP://usabrbmsdct005.uno.adt.bms.com:636']
    from_split = from_to[0].split('=')
    from_server = clean_server_name(from_split[1]).replace("'","")
    from_connector = get_connector_from_address(from_server)

    to_split = from_to[1].split('=')
    to_server = clean_server_name(to_split[1]).replace("'","")
    to_connector = get_connector_from_address(to_server)
    return f'{from_connector}-->{to_connector}'
 
def rq(s):
    # remove quotes
    s = s.replace('"','')
    s = s.replace("'","")
    return s

def print_flow_rules(d_rule_mappings):
    #print(f'FLOW RULES: {d_rule_mappings}')
    print('FLOW RULES:')
    for k,v in d_rule_mappings.items():
        print(f'  {k}') # flow rule
        #print(v)
        for item in v:
            #print(f'{item.keys()}',end = ' ') 
            if "direction" in item:
                print(f'    direction:{item["direction"]}')
            if "mapping" in item:
                print(f'    {rq(item["mapping"][0])}-->{rq(item["mapping"][1])}')
            if "config" in item:
                print(f'    config: {item["config"]}')
            if "requires" in item:
                print(f'    requires: {item["requires"]}')
            if "output" in item:
                print(f'    output: {item["output"]}')
            if "flow_criteria" in item:
                print(f'    flow_criteria: {item["flow_criteria"]}')
            if "from_to" in item:
                print(f'    {clean_from_to(item["from_to"],k)}')
        #mapping = v[0]['mapping']
        #print(f'{mapping[0]}-->{mapping[1]}')
        #print(f'{v["mapping"][0]}-->{v["mapping"][1]}')

def clean_string(s):
    s = s.replace('"','')
    s = s.lower()
    return s

def get_mappings_values(d_rule_mappings):
    all_values = set()
    for mapping_key in d_rule_mappings:
        for item in d_rule_mappings[mapping_key]:
            #print(item.keys(),item.values())
            if 'mapping' in item:
                for v in item.values():
                    all_values.add(clean_string(v[0]))
                    all_values.add(clean_string(v[1]))
    return list(all_values)


def my_compare(results,check,attrib_name):
    raw = str(results)
    if check in raw:
        #print(f"FOUND RAW {raw}")
        if (attrib_name not in results) or (results[attrib_name] == None):
            return False
        return True
    return False


def get_constructed_attrib_rule(r):
    # format for r {"cn":"xxx","entrydn":"yyy"}
    entry_dn = r['entrydn']
    entry_dn = entry_dn.replace('cn=','')
    entry_split = entry_dn.split(',')
    return entry_split[1] + '.' + entry_split[0]

def get_constructed_attributes(login_creds, d_rule_mappings):
    d_constructed_attribs = defaultdict(list) 
    search_base = 'cn=Constructed Attributes,cn=Shared Configuration,cn=JoinEngine Configuration,ou=InJoinv8,ou=Config,o=bms.com'
    search_filter = '(objectClass=mdsGrammarConstructedAttributeRule)'
    # attrs = ['cn','mdsrulesetlist']
    attrs = ['entrydn','mdsgenericrulerequirements','mdsgenericrulesubstitution','mdsgenericruleformat','cn']
    mapping_values = get_mappings_values(d_rule_mappings)
    print(f'Constructed Attribute mapping_values: {mapping_values}')
    _,results = paged_search(login_creds, search_base, search_filter, search_scope, attrs, dereference_aliases=DEREF_ALWAYS)
    found_rule = False
    for r in results:
        rule_name = get_constructed_attrib_rule(r)
        for check in mapping_values:
            c = my_compare(r,check,'mdsgenericrulerequirements')
            if c:
                #print(f'RULE {rule_name}')
                #print('  REQUIRES: ',r['mdsgenericrulerequirements'])   
                d_constructed_attribs[rule_name].append({'requires':r['mdsgenericrulerequirements']})
                found_rule = True
            c = my_compare(r,check,'mdsgenericrulesubstitution')
            if c:
                #if not found_rule:
                #    print(f'RULE  {rule_name}')
                #print('  OUTPUT: ',r['mdsgenericrulesubstitution'])    
                d_constructed_attribs[rule_name].append({'output':r['mdsgenericrulesubstitution']})
                found_rule = True
            c = my_compare(r,check,'mdsgenericruleformat')
            if c:
                #if not found_rule:
                #    print(f'RULE  {rule_name}')
                #print('  FORMAT: ',r['mdsgenericruleformat'])
                d_constructed_attribs[rule_name].append({'format':r['mdsgenericruleformat']})
    return d_constructed_attribs

def print_constructed_attribs(d_constructed_attribs):
    #print(d_constructed_attribs)
    print('Constructed Attributes:')
    for k,v in d_constructed_attribs.items():
        print(f'  {k}')
        for param in v:
            for action,value in param.items():
                if value:
                    print(f'    {action}:{value}')

def get_connectors():
    # get connector name and data server address

    search_base = 'cn=Connector Views,cn=JoinEngine Configuration,ou=InJoinv8,ou=Config,o=bms.com'
    search_filter = '(objectclass=mdscv)'
    # attrs = ['cn','mdsrulesetlist']
    attrs = ['mdscvid','mdsviewlocation','cn']
    _,results = paged_search(login_creds, search_base, search_filter, search_scope, attrs, dereference_aliases=DEREF_ALWAYS)
    d = result_to_dict(results)
    d_connectors = {}
    for connector in d:
        if 'mdscvid' in connector:
            id = connector['mdscvid']
            d_connectors[id] = {'description':connector['cn'][0], 'server':connector['mdsviewlocation']}
        # for k,v in connector.items():
        #     #d_connectors[k] = {'description':v['cn'],'server':v['mdsviewlocation']}
        #     d_connectors[k] = v
    return d_connectors

def print_connectors(d_connectors):
    print('CONNECTORS: ')
    for k,v in d_connectors.items():
        #print('  ',k,v)
        print(f'   {k}',end=' ')
        print(f'description: {v["description"]}, server: {clean_server_name(v["server"])}')

    
search_scope = SUBTREE
if __name__ == "__main__":
    # main section
    # get command line arguments and put into dict
    get_command_line_args()
    print(f'd_cmd_args: {d_cmd_args}')
    # TODO make this base64
    if 'env' in d_cmd_args and d_cmd_args['env'].lower() == 'uat':
        login_creds = 'metaview-uat.bms.com|cpjevkstag|cn=join engine,ou=nonpeople,o=bms.com|10389'
    else:
        login_creds = 'metaview.bms.com|cpjevkprod|cn=join engine,ou=nonpeople,o=bms.com|10389'
    d_connectors = get_connectors()
    if 'show_constructed_attributes' in d_cmd_args:
        print_connectors(d_connectors)
    if 'attribute' in d_cmd_args:
        d_rule_mappings = get_mapping_rules_and_mappings(login_creds)
        #print(json.dumps(d_rule_mappings,indent=2))
        get_flow_rules(login_creds, d_rule_mappings)
        print_flow_rules(d_rule_mappings)
    #d_constructed_attribs = get_constructed_attributes(login_creds, d_rule_mappings)
    #print_constructed_attribs(d_constructed_attribs)
