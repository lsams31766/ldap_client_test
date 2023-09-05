#flask interface to the rules filter code
from flask import Flask, redirect, url_for, render_template, request
import sys
sys.path.append('../')
from ldap_client import *
from ldap3 import MODIFY_REPLACE, SUBTREE
app = Flask(__name__)

### LDAP processing routines
prod_dirs = [
  {'name':'access management','creds':'edir01','search_base':'o=bms.com'},
  {'name':'enterprise directory ','creds':'enterprise','search_base':'o=bms.com'},
  {'name':'meta-supplier','creds':'meta-supplier','search_base':'o=bms.com'},
  {'name':'one','creds':'adjoin-na','search_base':'DC=one,DC=ads,DC=bms,DC=com'},
  {'name':'forge rock unified','creds':'frds','search_base':'o=bms.com'},
  {'name':'metaview','creds':'metaview','search_base':'o=bms.com'}  
]

def get_prod_dir_for_name(dir_name, env_selected):
    if env_selected == 'PROD':
        cur_dirs = prod_dirs
    elif env_selected == 'UAT':
        cur_dirs = uat_dirs    
    else:
        print('BAD ENVIRONMENT selected')
        return    
    for d in cur_dirs:
        if d['name'] == dir_name:
            return d
    return None

other_prod_dirs = [
  {'name':'celcorp','creds':'uslvlspadsadc01','search_base':'DC=celgene,DC=com'},
]

uat_dirs = [
  {'name':'access management','creds':'smlxpolhr81','search_base':'o=bms.com'},
  {'name':'enterprise directory','creds':'enterprise-uat','search_base':'o=bms.com'},
  {'name':'meta-supplier','creds':'metaqa-supplier','search_base':'o=bms.com'},
  {'name':'uno','creds':'uno','search_base':'DC=one,DC=ads,DC=bms,DC=com'},
  {'name':'forge rock qa','creds':'dsusr-1-r1-qa','search_base':'o=bms.com'},
  {'name':'metaview-uat','creds':'metaview-uat','search_base':'o=bms.com'},
]

dir_servers_chosen = []
def get_dir_servers_selected(env_selected):
    # assuming we are doing prod lookups
    servers = []
    if env_selected == 'PROD':
        cur_dirs = prod_dirs
    elif env_selected == 'UAT':
        cur_dirs = uat_dirs    
    else:
        print('BAD ENVIRONMENT selected')
        return
    all_checked = True
    for item in cur_dirs:
        if item['name'] in dir_servers_chosen:
            servers.append({'name':item['name'],'checked':True})
        else:
            servers.append({'name':item['name'],'checked':False})
            all_checked = False
    # add the all button, determine if it should be checked
    servers.append({'name':'ALL/NONE','checked':all_checked})
    return servers

def clean_entry(token):
    # eitherh line: 'mail'
    # or  ['Moonmoon.Kazi@bms.com']
    # get rid of unnecessary characters
    if type(token) == list and len(token) == 1:
        v = str(token)
        v = v.replace('[','')
        v = v.replace(']','')
    else:
        v = str(token)
    v = v.replace("'",'')
    return v

def sort_output(d_results, attrs):
    if type(d_results) == dict:
        return d_results # nothing to sort
    out_list = []
    print(f'++attrs {attrs}')
    for attr in attrs:
        if d_results:
            local_list = list(filter(lambda d: attr in d, d_results)) #get items that have attr as a key
            #print(f'++local_list before sort {local_list}')
            d_results = list(filter(lambda d: attr not in d, d_results))  #remove items attr is not a key
            # if value is a list, use first value as sort criteria
            #print(f'++++sort this: {local_list}+++')
            #print('++++++')
            try: # assume sort key not a list
                local_list = sorted(local_list, key=lambda d: d[attr].lower()) # sort that list
            except: # sort key must be a list
                local_list = sorted(local_list, key=lambda d: d[attr][0].lower()) # sort that list
            # print(f'++local_list after sort {local_list}')
            out_list.extend(local_list) # add to final list
            # print(f'++new out_list {out_list}')
    if d_results:
        out_list.extend(d_results) # add any left over items
    return out_list

def format_output(server, results, attrs):
    # txt_out += s + ': ' + str(result_to_dict(results)) + '\n
    d_results = result_to_dict(results)
    if type(d_results) == dict:
        out_str = server + ':' + '\n'
        for k,v in d_results.items():
            out_str += '   ' + clean_entry(k) + ': ' + clean_entry(v)
        out_str += '\n'
        return out_str
    # list so put sub entrys on new lines with indent
    d_results = sort_output(d_results, attrs)
    out_str = server + ':' + '\n'
    for item in d_results:
        # out_str += '   ' + str(item) + '\n'
        for a in attrs:
            if a in item:
                out_str += '   ' + clean_entry(a) + ': ' + clean_entry(item[a])
        out_str += '\n'
    return out_str

def process_query(servers_selected, new_attributes, new_filter,env_selected):
    # return text field for search of given attributes on givem servers
    # for each search, we need: dir_creds, search_base, search_filter, attributes
    # do some validation 
    set_terminate_on_error(False) # don't quit if ldap fails

    #print(f'process_query SS:{servers_selected} NA:{new_attributes} NF:{new_filter}')
    if not servers_selected:
        return 'ERROR - can not search - Select one or more servers'
    if new_attributes == '*':
        return 'ERROR - need one or more attributes, can not search for all attributes'
    if new_attributes == '':
        return 'ERROR - need one or more attributes'
    # new_filter needs to be in form: attr=x OR attr=[x,y,z...]
        return 'ERROR - need one or more attributes'
    if '=' not in new_filter :
        return 'ERROR - search criteria, Missing =, format must be attr=x OR attr=[x,y,z...]'
    f_split = new_filter.split('=')
    #print(f'==> TYPE {type(f_split[1])}')
    if (type(f_split[1]) != str) and (type(f_split[1]) != list):
        return 'ERROR - search criteria format must be attr=x OR attr=[x,y,z...]'
    new_filter = "(" + new_filter + ")"
    # need this format: new_attributes = ['uid','cn']
    attr_list = new_attributes.split(',')
    #print(f'==>new_attributes {attr_list}')
    # now do each search
    txt_out = ''
    search_scope = SUBTREE
    for s in servers_selected:
        if s == 'ALL/NONE':
            continue
        # print(f'-->{s}<--')
        d = get_prod_dir_for_name(s,env_selected)
        if not d or len(d.keys()) == 0:
            print('NO CREDS FOR ',s)
            return
        dir_creds = get_creds_from_server(d['creds'])
        # print(f'-->dir_creds {dir_creds}')
        # print(f'==>new_filter {new_filter}')
        r,results = paged_search(dir_creds, d['search_base'], 
        new_filter, search_scope, attr_list)
        # for now do raw output - TODO format this output
        #print(f'search results {results} r {r}')
        #txt_out += s + ': ' + str(result_to_dict(results)) + '\n'\
        txt_out += format_output(s, results, attr_list)
    #print(f'==>{txt_out}<==')
    return txt_out

#### HTML route routines
attribute_selected = '-'
search_critera_chosen = 'bmsid=*'
env_selected = 'PROD'

@app.route("/", methods = ['POST', 'GET'])
def index():
    global dir_servers_chosen, attribute_selected, search_critera_chosen
    global env_selected
    servers_selected = get_dir_servers_selected(env_selected)    
    #print(servers_selected)
    if request.method == "POST":
        d = request.form.to_dict()
        # print(f'POST got {d}')
        # FORMAT: {'meta-supplier': '1', 'one': '1', 'forge rock unified': '1', 'metaview': '1', 
        # 'submit': 'Post', 'set_attributes': 'password', 'set_criteria': 'bmsid=2027'}
        # get the servers selected
        dir_servers_chosen = []
        server_names = [i['name'] for i in servers_selected]
        for n in d.keys():
            if n in server_names:
                dir_servers_chosen.append(n)
        env_selected = d['environment']
        new_attributes = d['set_attributes']
        new_filter = d['set_criteria']
        servers_selected = get_dir_servers_selected(env_selected)
        servers_to_search = [s['name'] for s in servers_selected if s['checked']==True]
        # process query only if btnSubmit clicked
        filter_output='None'
        if 'btnSubmit' in d.keys():
            filter_output = process_query(servers_to_search, new_attributes, new_filter,env_selected)
        return render_template("index.html",
            servers_selected=servers_selected,
            attribute_selected=new_attributes,
            search_critera_chosen=new_filter,
            filter_output=filter_output,
            env_selected=env_selected)
    return render_template("index.html",
        servers_selected=servers_selected,
        attribute_selected=attribute_selected,
        search_critera_chosen=search_critera_chosen,
        filter_output='None',
        env_selected=env_selected)
 
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
