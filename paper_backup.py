import argparse
import time
import base64
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
    
    # store to file
    store_passphrase(words)
    time.sleep(0.5)
    # encrypt 
    gpg_encrypt(words)
    time.sleep(0.5)
    # shred
    shred_cache()
    qr_code()
    qr_code_short_hash()
    
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
def hash_qrcode(target, ask_hash):
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
    time.sleep(0.2)
    print(Fore.RESET+ Back.RESET+ f'\nLong sha256: {long_hash}')
    # short has
    short_str = ''
    for i in range(0, len(long_hash) - 1):
        short_str += long_hash[i]
        if i == 21:
            break;
    print(f'Short sha256: {short_str}')
    
    # compare hash 
    if ask_hash == 'q' or ask_hash == 'Q':
        print(Fore.RED+Back.RESET+ '\nskip _nothing to compare hash.')
    elif short_str == ask_hash or long_hash == ask_hash:
        print(Fore.GREEN+ '\nCompare Hash: True')
        print(f'Hash: {short_str}\nPrev Hash: {ask_hash}')
    else:
        print(Fore.RED+ '\nCompare Hash: False')
    
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
            print(Fore.GREEN+ f'show: ' +Back.WHITE+Fore.BLACK+ f'{passphrase_Q}' +Back.RESET)
            pending = 1
        elif qna == 'n' or qna == 'N':
            print(Fore.GREEN+ f'show: '+ Fore.RED+Back.WHITE+ 'nope im hide.'+Back.RESET)
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
                print(Fore.RED+ '\nError check Q list none numeric.\n')
                break
                
            
    trg_img = f'qrcode/{trg_Q}'
    zbarimg_cmd = ['zbarimg','--nodisplay','--nodbus','--quiet',f'{trg_img}']
    zbarimg_sub = subprocess.Popen(zbarimg_cmd, stdout = subprocess.PIPE)
    zbarimg_str = str(zbarimg_sub.communicate())
    get_gpg = zbarimg_str.replace('(b\'QR-Code:','').replace('\', None)','').split('\\n')
    
    # print out gpg & write to file
    file_open = open('qrcode_decode.gpg', 'w')
    try:
        print(Fore.BLUE+ '\n*scanning qrcode')
        for i in range(0,5):
            time.sleep(0.5)
            print('***', end='', flush=True)
        print('\n')
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
    
    # # hash qrcode (just get the hash, manual checking)
    # _wait = 0
    # while _wait != 1:
    #     ask_hash = str(input(Fore.RESET+Back.RESET +'Input prev hash or [q/Q] to skip: '))
    #     if ask_hash == '':
    #         _wait = 0
    #     elif ask_hash == 'q' or ask_hash == 'Q':
    #         _wait = 1
    #     else:
    #         _wait = 1
    
    # hash_qrcode(get_gpg, ask_hash)
    
    
    # hash qrcode (just get the hash, auto checking)
    if trg_Q:
        name_qrcode = trg_Q.split('-')
        hash_qrcode(get_gpg, name_qrcode[0])
    else:
        print(Fore.RED+ 'ERROR trg_Q not found for comparing hash')
        
    # decrypt_qrcode
    print('\n')
    decrypt_qrcode_gpg()
    print(Fore.BLUE+ Back.RESET+ '\ndecrypt succeed.')
    
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
    
    
# Mini conversion tools
def _convert_text_to_all(args):
    print(Fore.YELLOW+'\nI Have No Idea What These Is.\n')
    pick = int(input(Fore.RESET+'1. Text-Base64-ROT13\n2. ROT13-Base64-Text\n3. Develope only [Testing]\n\nchose: '))
    
    binary = _tobinary(args)
    dec = _todecimal(binary)
    hex = _tohex(dec)
    base64 = _encode_base64(args)
    encrypt_rot13 = _ROTCipher('encrypt', args, 13)
    vigenre = _vigenre_cipher(args)
    
    if pick == 1:
        tbr = _ROTCipher('encrypt', base64, 13)
        print('|')
        print(f'|_{base64}')
        print('|_Text-Base64-ROT13: '+Fore.BLACK+Back.WHITE+ f'{tbr}' + Back.RESET+Fore.RESET)
        
    elif pick == 2:
        rbt = _ROTCipher('decrypt', args, 13)
        rbt_text = _decode_base64(rbt)
        print('|')
        print(f'|_{rbt}')
        print('|_ROT13-Base64-Text: '+Fore.BLACK+Back.WHITE+ f'{rbt_text}' + Back.RESET+Fore.RESET)
    elif pick == 3:
        print('|')
        print('|________text: '+Fore.BLACK+Back.WHITE+ f'{args}' + Back.RESET+Fore.RESET)
        print('|')
        print('|______binary: '+Fore.BLACK+Back.WHITE+ f'{binary}' + Back.RESET+Fore.RESET)
        print('|')
        print('|_____decimal: '+Fore.BLACK+Back.WHITE+ f'{dec}' + Back.RESET+Fore.RESET)
        print('|')
        print('|_hexadecimal: '+Fore.BLACK+Back.WHITE+ f'{hex}' + Back.RESET+Fore.RESET)
        print('|')
        print('|______base64: '+Fore.BLACK+Back.WHITE+ f'{base64}' + Back.RESET+Fore.RESET)
        print('|')
        print('|_______ROT13: '+Fore.BLACK+Back.WHITE+ f'{encrypt_rot13}' + Back.RESET+Fore.RESET)
        print('|')
        print('|_____vigenre: '+Fore.BLACK+Back.WHITE+ f'{vigenre}' + Back.RESET+Fore.RESET)

# text to binary    
def _tobinary(text):
    if not text:
        return Fore.RED+ 'variable _tobinary() : false'
    text_str = str(text)
    result = ''.join(format(i, '08b') for i in bytearray(text_str, encoding ='utf-8'))
    
    return str(result)

# text to decimal
def _todecimal(_binary):
    _dec = int(_binary, 2)
    return _dec

# dec to hex
def _tohex(dec):
    _dec_int = int(dec)
    _hex_str = str(hex(_dec_int))
    return _hex_str

# text to encode base64
def _encode_base64(text):
    _str_bytes = text.encode('ascii')
    _base64 = base64.b64encode(_str_bytes)
    _base64_str = _base64.decode('ascii')
    return _base64_str

# decode base64 to text
def _decode_base64(text):
    _str_bytes = text.encode('ascii')
    _base64 = base64.b64decode(_str_bytes)
    _base64_str = _base64.decode('ascii')
    return _base64_str

# text to ROT13
def _ROTCipher(action, text, shift):
    _strUpper = text.upper()
    # Dictionary to lookup the index of alphabets
    dict1 = {'A' : 1, 'B' : 2, 'C' : 3, 'D' : 4, 'E' : 5,
            'F' : 6, 'G' : 7, 'H' : 8, 'I' : 9, 'J' : 10,
            'K' : 11, 'L' : 12, 'M' : 13, 'N' : 14, 'O' : 15,
            'P' : 16, 'Q' : 17, 'R' : 18, 'S' : 19, 'T' : 20,
            'U' : 21, 'V' : 22, 'W' : 23, 'X' : 24, 'Y' : 25, 'Z' : 26}
    
    # Dictionary to lookup alphabets
    # corresponding to the index after shift
    dict2 = {0 : 'Z', 1 : 'A', 2 : 'B', 3 : 'C', 4 : 'D', 5 : 'E',
            6 : 'F', 7 : 'G', 8 : 'H', 9 : 'I', 10 : 'J',
            11 : 'K', 12 : 'L', 13 : 'M', 14 : 'N', 15 : 'O',
            16 : 'P', 17 : 'Q', 18 : 'R', 19 : 'S', 20 : 'T',
            21 : 'U', 22 : 'V', 23 : 'W', 24 : 'X', 25 : 'Y'}
    
    if action == 'encrypt':
        cipher = ''
        for index in range(0, len(_strUpper)):
            if _strUpper[index] in dict1:
                # checking for space
                if _strUpper[index] != ' ':
                    # looks up the dictionary and
                    # adds the shift to the index
                    num = ( dict1[_strUpper[index]] + shift ) % 26
                    # looks up the second dictionary for
                    # the shifted alphabets and adds them
                    # check capital letter
                    if text[index].isupper():
                        cipher += dict2[num].upper()
                    else:
                        cipher += dict2[num].lower()
                else:
                    # adds space
                    cipher += ' '
            else:
                cipher += text[index]
             
        return cipher
    
    elif action == 'decrypt':
        decipher = ''
        for index in range(0, len(_strUpper)):
            if _strUpper[index] in dict1:
                # checks for space
                if(_strUpper[index] != ' '):
                    # looks up the dictionary and
                    # subtracts the shift to the index
                    num = ( dict1[_strUpper[index]] - shift + 26) % 26
                    # looks up the second dictionary for the
                    # shifted alphabets and adds them
                    if text[index].isupper():
                        decipher += dict2[num].upper()
                    else:
                        decipher += dict2[num].lower()
                else:
                    # adds space
                    decipher += ' '
            else:
                decipher += text[index]
    
        return decipher
    else:
        return Fore.RED+ 'NO ACTION ROT13'
        
# Vigenère cipher
def _vigenre_cipher(text):
    # Python code to implement
    # Vigenere Cipher
    
    # This function generates the
    # key in a cyclic manner until
    # it's length isn't equal to
    # the length of original text
    def generateKey(string, key):
        key = list(key)
        if len(string) == len(key):
            return(key)
        else:
            for i in range(len(string) -
                        len(key)):
                key.append(key[i % len(key)])
        return("" . join(key))
        
    # This function returns the
    # encrypted text generated
    # with the help of the key
    def cipherText(string, key):
        cipher_text = []
        for i in range(len(string)):
            x = (ord(string[i]) +
                ord(key[i])) % 26
            x += ord('A')
            cipher_text.append(chr(x))
        return("" . join(cipher_text))
        
    # This function decrypts the
    # encrypted text and returns
    # the original text
    def originalText(cipher_text, key):
        orig_text = []
        for i in range(len(cipher_text)):
            x = (ord(cipher_text[i]) -
                ord(key[i]) + 26) % 26
            x += ord('A')
            orig_text.append(chr(x))
        return("" . join(orig_text))
    
    keyword  = 'NOWnothingfinderPersonPlaNet'
    key = generateKey(text, keyword)
    cipher_text = cipherText(text, key)
    _cipherText = str(cipher_text)
    return _cipherText +' and ->'+str(originalText(_cipherText, key))
        
        
# Initialize parser
parser = argparse.ArgumentParser(description = 'Paper backup -> ascii img')
 
# Adding optional argument
parser.add_argument('-bip39', '--BIP39', action='store_true', help = 'Encrypt Passphrase Wordlist Mnemonic BIP 39')
parser.add_argument('-eff', '--EFF', action='store_true', help = 'Encrypt passphrase Wordlist passphraseme')
parser.add_argument('-e', '--encrypt', default='', dest='encrypt', help='Encrypt text to AES256: *.py -e \'[string]\'', type=str)
parser.add_argument('-d', '--decrypt', action='store_true', help = 'Decrypt qrcode, etc')
parser.add_argument('-cvt','--convert', default='', dest='convert', help='Mini Conversion Tools')

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
elif args.convert:
    # print(Fore.RED+ f'\nMini Conversion Tools\nGet String: {args.convert}')
    _convert_text_to_all(args.convert)
else:
    print('No argument')
    
    
    
# mnemonic bip39 and validate

# show phasephrase

# encrypt phasephrase gpg
# ```
# gpg --batch --passphrase-fd 3 --s2k-mode 3 --s2k-count 65011712 --s2k-digest-algo sha512 --cipher-algo AES256 --symmetric --armor 3<<<'$passphrase'
# ```

# openssl dgst -sha512