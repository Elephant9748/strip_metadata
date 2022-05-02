import time
import os
import subprocess
import progressbar
import shutil
import glob
from colorama import Fore, Back, Style

# view_metada
def view_metada(cmd = ['ls', 'img/ori']):
    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE)
    pipe_proc = str(proc.communicate())
    q = pipe_proc.split('\\n')
    print(Fore.GREEN+ '\ncurrent directory')
    print(Fore.GREEN+ '*******************')
    for i in range(0, len(q) - 1 ):
        if i == 0:
            filter = q[i].replace('(b\'','')
            print(f'~ {filter}')
        else:
            print(f'~ {q[i]}')
            
    # get file name        
    res = input(Fore.WHITE+ '\ntype file name or press enter (all file): ')
    
    # run exiftool
    cmd = ['exiftool']
    cmd.append(f'img/ori/{res}')
    header = Fore.MAGENTA+ f'\nMetadata all img' if res == '' else f'\nMetadata of {res}'
    print(header)
    line = ''
    for i in range(0, len(header) - 1):
        line += '*'
    print(line)
    exif = subprocess.Popen(cmd, stdout = subprocess.PIPE)
    exif_proc = str(exif.communicate())
    trim1 = exif_proc.split('\\n')
    for i in range(1, len(trim1) - 1):
        print(Fore.CYAN+ f'{trim1[i]}')

# view metadata out
def view_metada_out(cmd = ['ls', 'img/out']):
    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE)
    pipe_proc = str(proc.communicate())
    q = pipe_proc.split('\\n')
    print(Fore.GREEN+ '\ncurrent directory')
    print(Fore.GREEN+ '*******************')
    for i in range(0, len(q) - 1 ):
        if i == 0:
            filter = q[i].replace('(b\'','')
            print(f'~ {filter}')
        else:
            print(f'~ {q[i]}')
            
    # get file name        
    res = input(Fore.WHITE+ '\ntype file name or press enter (all file): ')
    
    # run exiftool
    cmd = ['exiftool']
    cmd.append(f'img/out/{res}')
    header = Fore.MAGENTA+ f'\nMetadata all img' if res == '' else f'\nMetadata of {res}'
    print(header)
    line = ''
    for i in range(0, len(header) - 1):
        line += '*'
    print(line)
    exif = subprocess.Popen(cmd, stdout = subprocess.PIPE)
    exif_proc = str(exif.communicate())
    trim1 = exif_proc.split('\\n')
    for i in range(1, len(trim1) - 1):
        print(Fore.CYAN+ f'{trim1[i]}')

def strip_metadata(cmd = ['exiftool']):
    cmd.append(f'-all=')
    cmd.append(f'img/ori')
    strip = subprocess.Popen(cmd, stdout = subprocess.PIPE)
    strip_proc = str(strip.communicate())
    trim1 = strip_proc.split('\\n')
    print(Fore.CYAN+ '\nlog: ')
    print('+--+')
    for i in range(1, len(trim1) - 1):
        print(trim1[i].strip())
    
    #ls img
    time.sleep(0.4)
    cmd_dir = ['ls','img/ori']
    out_dir = subprocess.Popen(cmd_dir, stdout = subprocess.PIPE)
    out_dir_proc = str(out_dir.communicate())
    trim = out_dir_proc.split('\\n')
    print(Fore.YELLOW+'+-----------+')
    print(Fore.YELLOW+'list img/ori:')
    print(Fore.YELLOW+'+-----------+')
    img_ext_list = ['jpg','jpeg','png','raw','bmp','svg','gif','webp']
    img_ext = []
    for i in range(0, len(trim) - 1):
        log = trim[i].strip().replace('(b\'','') if i == 0 else trim[i].strip()
        for j in range(0, len(img_ext_list) - 1):
            if img_ext_list[j] in log:
                img_ext.append(img_ext_list[j]) 
        print(Fore.GREEN+ f'* {log}')
    print(Fore.RESET+'+-----------+')
    print(Fore.BLUE+ f'*current images support (edit on img_ext_list): {img_ext_list}')
    
    rm_img_ext_duplicate = []
    [rm_img_ext_duplicate.append(x) for x in img_ext if x not in rm_img_ext_duplicate]
    
    # copy img to dir
    index = 0 
    while index < len(rm_img_ext_duplicate):
        for i in range(-1, len(rm_img_ext_duplicate) - 1):
            time.sleep(0.5)
            print('*', end='', flush=True)
        glob_files = glob.glob(f'img/ori/*.{rm_img_ext_duplicate[index]}')
        if not glob_files or glob_files == []:
            print(Fore.RED+ '\n[log] Break img files already exists on img/out')
            print(Fore.GREEN+'done... \n-checkout img/out...')
            break
        else:
            time.sleep(1)
            dest = 'img/out/'
            if index == 0:
                print('\ndelete prev out directory...')
                time.sleep(1)
                shutil.rmtree('img/out')
                print('\ncreate dir out...')
                parent_dir = 'img'
                path = os.path.join(parent_dir, 'out')
                os.mkdir('img/out')
            print('\nmove images to img/out...')
            time.sleep(1)
            print(glob_files)
            for img in glob_files:
                print(img)
                shutil.move(img,dest)
            print(Fore.GREEN+ 'done... \n-checkout img/out...')
        index += 1

def go_():
    chose = int(input('\noption menu: \n\n1. view metadata [img/ori] \n2. strip all metadata [img/ori] \n3. view metada on [img/out]\n\nchose option: '))
    
    if chose  == 1:
        # print('view...>')
        view_metada()
    elif chose == 2:
        # print('strip metadata ...>')
        strip_metadata()
    elif chose == 3:
        view_metada_out()
    else:
        print('option not found ....')
    
go_()

