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
    time.sleep(0.5)
    gpg_encrypt(wordlist_trim)
    
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
    store = open('file', 'w')
    try:
        store.write(f'{pphrase}')
    except:
        print(Fore.BLUE+ 'Error store_passphrase')
    finally:
        print(Fore.BLUE+ f'write files closed ...')
        shredin
        store.close()
        
        

# GPG symmetric AES256 encrypt
# echo 'secret' | gpg  --yes --batch --passphrase-fd 0 --symmetric --s2k-mode 3 
# --s2k-count 65011712 --s2k-digest-algo SHA512 --cipher-algo AES256 --armor <<< text-encrypted-here.......

def gpg_encrypt(passphrase):
    # AES_passphrase = str(input(Fore.RESET+Back.RESET+ f'Input Passphrase on images file: '))
    # cmd = ['gpg','--yes','--batch','--passphrase-fd 0','--symmetric',
    #        '--s2k-mode 3','--s2k-count 65011712','--s2k-digest-algo SHA512','--cipher-algo AES256',
    #        f'--armor ','<<<',f'{passphrase}']
    # cmd_str = f'echo \'{AES_passphrase}\' | gpg  --yes --batch --passphrase-fd 0 --symmetric --s2k-mode 3 --s2k-count 65011712 --s2k-digest-algo SHA512 --cipher-algo AES256 --armor <<< {passphrase}'
    
    # pipe to file
    # cmd = ['bash']
    # cmd = ['echo']
    # cmd.append(f' \"{passphrase}\"')
    # cmd.append('|')
    # cmd.append('gpg')
    cmd = ['gpg']
    # cmd.append('--yes')
    # cmd.append('--batch')
    # cmd.append('--passphrase-fd')
    # cmd.append('0')
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
    cmd.append('file')
    # cmd.append('<<<')
    # cmd.append(f'"{passphrase}"')
    # cmd_run = subprocess.run(cmd, capture_output = True)
    # print(cmd_run)
    cmd_run = subprocess.Popen(cmd, stdout = subprocess.PIPE)
    cmd_str = str(cmd_run.communicate())
    print(cmd_str)
    
    # data, temp = os.pipe()
    
    # os.write(temp, bytes('5 10\n','utf-8'))
    # os.close(temp)
    # s = subprocess.check_output(cmd_str, stdin = data, shell = True)
    # print(s.decode('utf-8'))


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
    


            
    