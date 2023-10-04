#celgene_report.py
''' script to change report celgene users in enterprise directory
  requires an excel file - File format:
  hCel UserID
  USERA
  USERB
  ...
  COMMAND LINE ARGUMENTS
  -i <filenmae>: Input XLSX file of Celgene users
'''
import sys
from ldap_client import *
from ldap3 import SUBTREE
import time
import openpyxl 

def print_help():
    print('''Invalid Operation:
python3 celgene_report.py -i<input xlsx fiename> -o<output xlsx filename>
    ''')
    print('Example: python3 celgene_report.py -i p1.xlsx -o p2.xlsx')

def get_command_line_args():
    #print(f'Number of arguments:  {len(sys.argv)} arguments.') 
    #print(f'Argument List:  {str(sys.argv)}')
    # required 2 arguments
    if len(sys.argv) < 3:
        print_help()
        exit(1)
    input_xlsx,output_xlsx = None,None
    dir_server = 'enterprise'
    i = 1
    while i < len(sys.argv):
        cmd = sys.argv[i]
        val = sys.argv[i+1]
        if cmd == '-i':
            input_xlsx = val
        if cmd == '-o':
            output_xlsx = val
        i += 2
    if (input_xlsx == None) or (output_xlsx==None):
        print_help()
        exit(1)
    return input_xlsx, output_xlsx, dir_server

def get_users_from_xslx_file(input_xlsx):
    ids = []
    wb = openpyxl.load_workbook(input_xlsx)
    ws = wb.active
    # top row should have 4 values, namely: 
    top_row = [ws.cell(row=1,column=i).value for i in range(1,2)]
    # print(top_row)
    expected_top_row = ['hCel UserID']
    if top_row != expected_top_row:
        print('Invalid file contents - STOPPING!')
    # read row by row until an empty cell is found
    row = 2
    while True:
        next_row = [ws.cell(row=row,column=i).value for i in range(1,2)]
        if (next_row[0] == None) or (next_row[0] == '') or (next_row[0] == ' '):
            break
        #print(next_row)
        ids.append(next_row[0])
        row += 1
    return ids

# now do the report
def make_report(ids,dir_creds,output_xlsx):
    book = openpyxl.Workbook()
    sheet = book.active
    top_row = ['employeeid','bmsid','mail','cn','bmsentaccoutstatus']
    sheet.append(top_row)
    search_filter = []
    search_scope = SUBTREE
    attrs = ['bmsid','mail','cn','bmsentaccountstatus']
    for id in ids:
        search_filter = f'(employeeid={id})'
        print(f'->FIND {id}')
        _,results = ldap_search(dir_creds, search_base_enterprise, search_filter, search_scope, attrs)
        #print(results) 
        # print the output row
        if results and (len(results) > 0):
            d = result_to_dict(results)
            if 'mail' not in d:
                d['mail'] = ''
            # format employeeid,bmsid,mail,cn,bmsentaccoutstatus
            output_row = [id,d["bmsid"],d["mail"],d["cn"],d["bmsentaccountstatus"]]
            print(output_row)
        else: # did not find name just output that
            output_row = [id]
        sheet.append(output_row)
    book.save(output_xlsx)


#--- COMMAND LINE PROCESSING ---#
input_xlsx, output_xlsx, dir_server = get_command_line_args()
ids = get_users_from_xslx_file(input_xlsx)
#exit(0)
dir_creds = get_creds_from_server(dir_server)
if dir_server == 'enterprise':
    search_base_enterprise  = 'o=bms.com'
else:
    print(f'SERVER {dir_server} not supported yet')
    exit(1)

#----- MAIN CODE -----#
# make the report
make_report(ids,dir_creds,output_xlsx)
print('DONE')
