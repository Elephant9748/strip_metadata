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
import hashlib
import io
import qrcode
import climage
import datetime
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
    qr_code()
    qr_code_short_hash()
    
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
        print(Fore.BLUE+ 'Shred unnecessary file')
        print(Fore.RED)
        shred = ['shred','-vuz','-n','10','frost', 'secret.gpg']
        shred_run = subprocess.Popen(shred, stdout = subprocess.PIPE)
        shred_stdin = str(shred_run.communicate())
        print(Fore.YELLOW+ f'{shred_stdin}')
        
    except:
        print(Fore.RED+ 'Shred ERROR')
    finally:
        print(Fore.GREEN+ 'Shred succeed')
    
# hash encrypted passphrase
def hash_me(hash_target):
    hash_target_str = ''
    for line in hash_target:
        hash_target_str += line
    
    hash = hashlib.sha256()
    target = hash_target_str.encode()
    hash.update(target)
    # long hash
    long_hash = hash.hexdigest()
    print(Fore.RESET+ f'\nLong hash sha256: {long_hash}')
    # short has
    short_str = ''
    for i in range(0, len(long_hash) - 1):
        short_str += long_hash[i]
        if i == 21:
            break;
    print(f'Short hash sha256: {short_str}')
    
    global short_hashing
    global long_hashing
    global hashing_str
    
    short_hashing = short_str
    long_hashing = long_hash
    hashing_str = hash_target_str

# qr_code include short hash
def qr_code_short_hash():
    # convert "qrcode/d44b4532e3f13bf9808d0f-date.png" -gravity center -scale 200% -extent 110% -scale 110% -gravity south -font /usr/share/fonts/truetype/noto/NotoMono-Regular.ttf -pointsize 48 -fill black -draw "text 0,50 'd44b4532e3f13bf9808d0f'" "qrcode/d44b4532e3f13bf9808d0f-date-by-convert.png"
    
    # short hash image
    print(Fore.BLUE+'\n*short hash qrcode. \n')
    
    convert_list = ['convert',
     f"qrcode/{long_hashing}-{current_time}-{name_image}.png",
     '-gravity','center','-scale','200%',
     '-extent','110%','-scale','110%',
     '-gravity','south',
     '-font','/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf',
     '-pointsize',' 48','-fill','black',
     '-draw',f"text 0,50 '{short_hashing}'",
     f'qrcode/{short_hashing}-{current_time}-{name_image}.png']
    
    convert_sub = subprocess.Popen(convert_list, stdout = subprocess.PIPE)
    pipe_str = str(convert_sub.communicate())
    print(pipe_str)
    print(Fore.YELLOW+ f'\nImage Path: qrcode/{short_hashing}-{current_time}-{name_image}.png')
    print(Fore.GREEN+ 'qr_code_short_hash succeed.')
    
# qr-code
def qr_code():
    
    global current_time 
    global name_image
    current_time = str(datetime.date.today())
    
    check = 0
    while check != 1:
        name_image = str(input(f'\ngive name to image: '))
        if name_image == '':
            check = 0
        else:
            check = 1
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(hashing_str)
    qr.make(fit=True)
    # qr.make(hashing_str)
    img = qr.make_image(fill_color='black', back_color='white')
    # img = qr.make_image()
    img.save(f'qrcode/{long_hashing}-{current_time}-{name_image}.png')
    
    # # qrcode ascii 
    # f = io.StringIO()
    # qr.print_ascii(out=f)
    # f.seek(0)
    # # print(Fore.RESET)
    # # for line in f:
    # #     print(line, end='', flush=True)
    # print(Fore.RED+ f.read())
    
    # climage
    out_image = climage.convert(f'qrcode/{long_hashing}-{current_time}-{name_image}.png', is_unicode=True, is_truecolor=False, is_256color=True, is_16color=False, is_8color=False, width=80, palette="default")
    
    print(out_image)
    print(Fore.YELLOW+ f'\nImage Path: qrcode/{long_hashing}-{current_time}-{name_image}.png')
    print(Fore.GREEN+ 'qr_code_hash succeed.')


def gpg_encrypt(passphrase):
    print(Fore.YELLOW+ 'encrypting passphare')
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
    
    for i in range(0, 5):
        time.sleep(0.5)
        print('*', end='', flush=True)
        
    print(Fore.YELLOW+ f'\n{cmd_str}')
    
    read = open('secret.gpg','r')
    lines = read.readlines()
    print(Fore.GREEN)
    try:
        for line in lines:
            print(line, end='', flush=True)
    except:
        print('ERROR open secret.gpg')
    finally:
        # hashing secret.gpg
        hash_me(lines)
        print(Fore.BLUE+ '\ngpg_encrypt succeed\n')
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
    


            
    