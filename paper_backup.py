# mnemonic bip39 and validate

# show phasephrase

# encrypt phasephrase gpg
# ```
# gpg --batch --passphrase-fd 3 --s2k-mode 3 --s2k-count 65011712 --s2k-digest-algo sha512 --cipher-algo AES256 --symmetric --armor 3<<<'$passphrase'
# ```

# openssl dgst -sha512

import argparse
import time
import subprocess
import os
from mnemonic import Mnemonic
from sys import exit
from colorama import Fore, Back

# BIP 39
# -------
def bip39():
    mnemo = Mnemonic('english')
    words = mnemo.generate(strength=256)
    print(f'Show BIP39 Mnemonic: '+ Fore.BLACK + Back.WHITE + f'{words}')
    print(Fore.GREEN+ '>>'+ Fore.RESET+ Back.RESET)
    
    # add here prompt input passphrase
    _clear()
    validate_phrase(words)
    
    
    for line in words:
        if not mnemo.check(line):
            exit(1)
            
    # seed = mnsemo.to_seed(words, passphrase='noidea nodiaeoidaoidoanodina')
    # print(seed)
    exit(0)

# EFF Wordlist
# ------------
def eff():
    cmd = ['passphraseme']
    option = input(Fore.RESET+ f'\n1. Use EFF\'s general large wordlist\n2. Use EFF\'s general short wordlist (default)\n3. Use EFF\'s short wordlist with unique prefixes\n\nchose: ')
    cmd.append('-l' if option == '1' else '-s2' if option == '3' else '-s1')
    entropy = input(Fore.RESET+ f'Bits of entropy/word: ')
    cmd.append('10' if not entropy else str(entropy))
    print(Fore.CYAN+ f'\n- cmd parse: {cmd}')
    time.sleep(1)
    for i in range(0, 8):
        time.sleep(0.5)
        if i == 7:
            print(Fore.GREEN+ '---->',end='', flush=True)
            break
        print(Fore.GREEN+ '*****',end='', flush=True)
    wordlist = subprocess.Popen(cmd, stdout = subprocess.PIPE)
    wordlist_proc = str(wordlist.communicate())
    wordlist_trim = wordlist_proc.replace('(b\'','').replace('\\n\', None)','')
    print(Fore.GREEN+ f'\n\npassphraseme generate: {wordlist_trim}')
    input(Fore.WHITE+ f'\n- Press enter to continue? ')
    
    # add here clear history or screen
    _clear()
    validate_phrase(wordlist_trim)
    store_passphrase(wordlist_trim)
    time.sleep(1)
    gpg_encrypt(wordlist_trim)
    time.sleep(1)
    shred_cache()
    
#Validate passphrase
def validate_phrase(passphrase):
    print(Back.RESET+Fore.CYAN+ '- to show prev passphrase [q]')
    validate = input(Fore.RESET+ 'type passhrase again here to validate: ')
    
    if validate == passphrase:
        print(Fore.GREEN+ '- Passphrase Valid...')
    elif validate == 'q' or validate == 'Q':
        _clear()
        print(f'Show EFF Passphrase: '+Back.WHITE+Fore.BLACK+ f'{passphrase}')
        validate_phrase(passphrase)
    else:
        _clear()
        print(Fore.RED+ '- Passphrase Not validate...')
        validate_phrase(passphrase)

# store phrase to file        
def store_passphrase(pphrase):
    store = open('frost', 'w')
    try:
        store.write(f'{pphrase}')
    except:
        print(Fore.BLUE+ 'Error store_passphrase')
    finally:
        print(Fore.BLUE+ f'\nstore files closed ...')
        print(Fore.RESET)
        store.close()

# shred unnecessary file     
def shred_cache():
    try:
        # shred forst
        print(Fore.YELLOW+ '\nShred unnecessary file\n')
        shred = ['shred','-vuz','-n','10','frost', 'secret.gpg']
        shred_run = subprocess.Popen(shred, stdout = subprocess.PIPE)
        shred_stdin = str(shred_run.communicate())
        print(Fore.YELLOW+ f'{shred_stdin}')
        
    except:
        print(Fore.RED+ 'Shred ERROR')
    finally:
        print(Fore.GREEN+ 'Shred succeed')
    

def gpg_encrypt(passphrase):
    cmd = ['gpg']
    cmd.append('-o')
    cmd.append('secret.gpg')
    cmd.append('--symmetric')
    cmd.append('--s2k-mode')
    cmd.append('3')
    cmd.append('--s2k-count')
    cmd.append('65011712')
    cmd.append('--s2k-digest-algo')
    cmd.append('SHA512')
    cmd.append('--cipher-algo')
    cmd.append('AES256')
    cmd.append('--armor')
    cmd.append('frost')
    cmd_run = subprocess.Popen(cmd, stdout = subprocess.PIPE)
    cmd_str = str(cmd_run.communicate())
    time.sleep(1)
    print(Fore.YELLOW+ 'encrypting passphare')
    for i in range(0, 5):
        time.sleep(0.5)
        print('*', end='', flush=True)
        
    print(Fore.GREEN+ f'\n{cmd_str}')
    print(Fore.WHITE+ '\n* gpg_encrypt succeed\n')
    
    read = open('secret.gpg','r')
    try:
        for line in read:
            print(line, end='')
    except:
        print('ERROR open secret.gpg')
    finally:
        read.close()
        
#Clear Screen
def _clear():
    _ = subprocess.call('clear' if os.name == 'posix' else 'cls')

# Initialize parser
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument('-B', '--BIP39', action='store_true', help = 'Wordlist Mnemonic BIP 39')
parser.add_argument('-E', '--EFF', action='store_true', help = 'Wordlist passphraseme')
 
# Read arguments from command line
args = parser.parse_args()

if args.BIP39:
    # print(f'Mnemonic BIP 39: {args.BIP39}')
    bip39()
elif args.EFF:
    # print(f'Wordlist EFF: {args}')
    eff()
else:
    print('No argument')
    


            
    