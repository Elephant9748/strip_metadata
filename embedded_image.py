import time
import subprocess
import base64
import argparse
from colorama import Fore, Back

# _set function metadata
def _set():
    text = str(input(Fore.RESET+ '\nInput String: '))
    filename = str(input(Fore.RESET+ '\nInput Path Location an Image: '))
    set_list = ['exiftool',f'-Certificate=\'{text}\'', f'{filename}']
    set_sub = subprocess.Popen(set_list, stdout = subprocess.PIPE)
    set_log = str(set_sub.communicate())
    print(f'\n{set_log}')
    
# _get function metadata    
def _get():
    filename = str(input(Fore.RESET+ '\nInput Path Location an Image: '))
    get_list = ['exiftool','-Certificate',f'{filename}']
    get_sub = subprocess.Popen(get_list, stdout = subprocess.PIPE)
    get_log = str(get_sub.communicate())
    # out = get_log.replace('(b\'','').replace('\\n\', None)','')
    # _out = out.split(':')
    print(f'\n{get_log}')

parser = argparse.ArgumentParser(description = 'Embedded Text to Imagen, require install exiftool')

parser.add_argument('-set','--SET', dest='set', action='store_true', help = 'Embedded Certificate TAG to PNG')
parser.add_argument('-get','--GET', dest='get', action='store_true', help = 'Get Certificate TAG from PNG')


args = parser.parse_args()

if args.set:
    print(Fore.GREEN+ '\nSet...\n')
    _set()
elif args.get:
    print(Fore.GREEN+ '\nGet...\n')
    _get()
else:
    print(Fore.RED+ 'ERRO No Argument')


