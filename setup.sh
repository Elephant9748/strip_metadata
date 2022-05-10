#!/bin/bash

#Run all on sudo

# require latest gnupg

# sudo -p mkdir img
mkdir -p img/ori
mkdir -p img/out
mkdir -p qrcode

apt install python3-pip
apt install imagemagick-6.q16  
# sudo apt install imagemagick-6.q16hdri              
# sudo apt install graphicsmagick-imagemagick-compat
apt install zbar-tools

# require python3 and pip
pip install -r requirement.txt

# if using tails uncomment below
# remember to check update packages at pypi.org
# python3 -m pip install ./pypi/passphraseme-0.1.5.tar.gz
# python3 -m pip install ./pypi/climage-0.1.3.tar.gz


