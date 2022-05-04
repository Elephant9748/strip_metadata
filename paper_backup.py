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
    time.sleep(0.5)
    gpg_encrypt(wordlist_trim)
    time.sleep(0.5)
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
    
# hash passphrase
def hash_me(hash_target):
    hash_target_str = ''
    for line in hash_target:
        hash_target_str += line
    
    hash = hashlib.sha256()
    target = hash_target_str.strip()
    target2 = hash_target_str.encode()
    hash.update(target2)
    
    # long hash
    long_hash = hash.hexdigest()
    print(Fore.RESET+ f'\nLong sha256: {long_hash}')
    # short has
    short_str = ''
    for i in range(0, len(long_hash) - 1):
        short_str += long_hash[i]
        if i == 21:
            break;
    print(f'Short sha256: {short_str}')
    
    global short_hashing
    global long_hashing
    global hashing_str
    
    short_hashing = short_str
    long_hashing = long_hash
    hashing_str = hash_target_str

# qr_code include short hash
def qr_code_short_hash():
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
    print(Fore.RESET+ pipe_str)
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
    
    print('\n')
    print(out_image)
    print(Fore.YELLOW+ f'\nImage Path: qrcode/{long_hashing}-{current_time}-{name_image}.png')
    print(Fore.GREEN+ 'qr_code_hash succeed.')


def gpg_encrypt(passphrase):
    print(Fore.YELLOW+ 'encrypting passphare')
    for i in range(0, 5):
        time.sleep(0.5)
        print('****', end='', flush=True)
        
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
    

# hash qrcode check
def hash_qrcode(target):
    target.pop(-1)
    target.pop(-1)
    str = ''
    for line in target:
        if line == '':
            str += f'\n'
        else:
            str += f'{line}\n'
            
    hash_qrcode = hashlib.sha256()
    update_hash = str.strip()
    update_hash2 = str.encode()
    hash_qrcode.update(update_hash2)

    # long hash
    long_hash = hash_qrcode.hexdigest()
    print(Fore.RESET+ Back.RESET+ f'Long sha256: {long_hash}')
    # short has
    short_str = ''
    for i in range(0, len(long_hash) - 1):
        short_str += long_hash[i]
        if i == 21:
            break;
    print(f'Short sha256: {short_str}')
    
# shred file decrypt qrcode
def shred_cache_qrcode():
    try:
        # shred forst
        print(Fore.BLUE+ Back.RESET+ '\nShred unnecessary file from qrcode function')
        print(Fore.RED)
        shred = ['shred','-vuz','-n','10','qrcode_decode.gpg']
        shred_run = subprocess.Popen(shred, stdout = subprocess.PIPE)
        shred_stdin = str(shred_run.communicate())
        print(Fore.YELLOW+ f'{shred_stdin}')
        
    except:
        print(Fore.RED+ 'Shred ERROR')
    finally:
        print(Fore.GREEN+ 'Shred succeed')
    
# decrypt qrcode gpg
def decrypt_qrcode_gpg():
    qrcode_gpg_list = ['gpg','--decrypt','qrcode_decode.gpg']
    qrcode_gpg_sub = subprocess.Popen(qrcode_gpg_list, stdout = subprocess.PIPE)
    qrcode_gpg_str = str(qrcode_gpg_sub.communicate())
    
    passphrase_Q = qrcode_gpg_str.replace('(b\'','').replace('\', None)','')
    
    pending = 0
    while pending != 1:
        qna = input(Fore.RESET+ '\nshow passphrase [y/n]? ')
        if qna == 'y' or qna == 'Y':
            print(Back.WHITE+Fore.BLACK+ f'\n{passphrase_Q}\n')
            pending = 1
        elif qna == 'n' or qna == 'N':
            print(Fore.RED+ '\nnope im hide.\n')
            pending = 1
        else:
            pending = 0
            

# decrypt qrcode
def decrypt_qrcode():
    # clear screen
    _clear()
    
    # get list of qrcode
    ls_list = ['ls','qrcode']
    ls_sub = subprocess.Popen(ls_list, stdout = subprocess.PIPE)
    ls_str = str(ls_sub.communicate())
    ls_str_format = ls_str.replace('(b\'','').replace('\', None)','').split('\\n')
    print('\nls qrcode')
    print('---------')
    for line in range(0, len(ls_str_format) - 1):
        print(Fore.CYAN+ f'{line}. {ls_str_format[line]}')
    wait = 0 
    while wait != 1:
        Q = str(input(Fore.RESET+ f'\nchose file name by index or name: '))
        if Q == '':
            wait = 0
        else:
            wait = 1

    if Q.isnumeric():
        trg_Q = ls_str_format[int(Q)]
    else:
        # check Q is on list 
        for line in ls_str_format:
            if line == Q:
                trg_Q = Q
                break
            else:
                print(Fore.RED+ 'Error check Q list none numeric.\n')
                break
    
    trg_img = f'qrcode/{trg_Q}'
    zbarimg_cmd = ['zbarimg','--nodisplay','--nodbus','--quiet',f'{trg_img}']
    zbarimg_sub = subprocess.Popen(zbarimg_cmd, stdout = subprocess.PIPE)
    zbarimg_str = str(zbarimg_sub.communicate())
    get_gpg = zbarimg_str.replace('(b\'QR-Code:','').replace('\', None)','').split('\\n')
    
    # print out gpg & write to file
    file_open = open('qrcode_decode.gpg', 'w')
    try:
        print(Fore.BLUE+ '\n*get pgp\n')
        check = len(get_gpg) - 2
        for line in range(0, len(get_gpg) - 1):
            # print line
            print(Fore.GREEN+ f'{get_gpg[line]}')
            # write line to file
            file_open.write(f'{get_gpg[line]}\n')
            if line == check:
                break
    except:
        print(Fore.RED+ 'ERROR decrypt pgp')
    finally:
        file_open.close()
       
    decrypt_qrcode_gpg()
    # hash qrcode (just get the hash, manual checking)
    hash_qrcode(get_gpg)
    print(Fore.BLUE+ Back.RESET+ 'decrypt succeed.')
    # shred file
    time.sleep(0.5)
    shred_cache_qrcode()
    
# encrypt text arguemtn --encrypt
def _encrypt_string(env_string):
    print(Fore.BLUE+ '\n*encrypt string/text,file')
    print(Fore.RESET)
    for i in range(0, 5):
        time.sleep(0.5)
        print('****', end='', flush=True)
    
    # store text to frost
    store_passphrase(env_string)
    time.sleep(0.5)
    
    # gpg encrypt    
    terminal_list = ['gpg',
                     '-o',
                     'secret.gpg',
                     '--symmetric',
                     '--s2k-mode',
                     '3',
                     '--s2k-count',
                     '65011712',
                     '--s2k-digest-algo',
                     'SHA512',
                     '--cipher-algo',
                     'AES256',
                     '--armor',
                     'frost']
    terminal_sub = subprocess.Popen(terminal_list, stdout = subprocess.PIPE)
    terminal_str = str(terminal_sub.communicate())
    
    # indicate encrypt succeed
    print(Fore.YELLOW+ f'\n{terminal_str}')
    
    _read = open('secret.gpg','r')
    _lines = _read.readlines()
    print(Fore.GREEN)
    try:
        for line in _lines:
            print(line, end='', flush=True)
    except:
            print('ERROR open secret.pgp')
    finally:
            hash_me(_lines)
            print(Fore.BLUE+ '\ngpg_encrypt string succeed\n')
            _read.close()
    time.sleep(0.5)
    shred_cache()
    qr_code()
    qr_code_short_hash()
    
# Initialize parser
parser = argparse.ArgumentParser(description = 'Paper backup -> ascii img')
 
# Adding optional argument
parser.add_argument('-bip', '--BIP39', action='store_true', help = 'Encrypt Passphrase Wordlist Mnemonic BIP 39')
parser.add_argument('-eff', '--EFF', action='store_true', help = 'Encrypt passphrase Wordlist passphraseme')
parser.add_argument('-e', '--encrypt', default='', dest='encrypt', help='Encrypt text to AES256: *.py -e \'[string]\'', type=str)
parser.add_argument('-d', '--decrypt', action='store_true', help = 'Decrypt qrcode, etc')
 
# Read arguments from command line
args = parser.parse_args()

if args.BIP39:
    # print(f'Mnemonic BIP 39: {args.BIP39}')
    bip39()
elif args.EFF:
    # print(f'Wordlist EFF: {args}')
    eff()
elif args.decrypt:
    decrypt_qrcode()
elif args.encrypt:
    # print(Fore.GREEN+ f'{args.encrypt}')
    _text_input = str(args.encrypt)
    _encrypt_string(_text_input)
else:
    print('No argument')
    


# mnemonic bip39 and validate

# show phasephrase

# encrypt phasephrase gpg
# ```
# gpg --batch --passphrase-fd 3 --s2k-mode 3 --s2k-count 65011712 --s2k-digest-algo sha512 --cipher-algo AES256 --symmetric --armor 3<<<'$passphrase'
# ```

# openssl dgst -sha512